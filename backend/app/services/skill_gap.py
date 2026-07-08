import json
import re
import tomllib
from pathlib import Path


def _read_requirements_txt(path: Path) -> set[str]:
    skills = set()
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9_.\-]+)", line)
        if match:
            skills.add(match.group(1))
    return skills


def _read_pyproject_toml(path: Path) -> set[str]:
    try:
        data = tomllib.loads(path.read_text(errors="ignore"))
    except tomllib.TOMLDecodeError:
        return set()

    skills = set()
    for dep in data.get("project", {}).get("dependencies", []):
        match = re.match(r"^([A-Za-z0-9_.\-]+)", dep)
        if match:
            skills.add(match.group(1))

    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    skills.update(name for name in poetry_deps if name.lower() != "python")
    return skills


def _read_package_json(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(errors="ignore"))
    except json.JSONDecodeError:
        return set()

    skills: set[str] = set()
    for section in ("dependencies", "devDependencies"):
        skills.update(data.get(section, {}).keys())
    return skills


_CANONICAL_LABELS = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "docker": "Docker",
}


def _dedupe_case_insensitive(skills: set[str]) -> set[str]:
    """A manifest's own dependency list can name a language marker we also
    add ourselves (e.g. a "typescript" devDependency alongside our
    "TypeScript" marker) — collapse those to one canonical label instead of
    showing both as separate skill chips."""
    by_lower: dict[str, str] = {}
    for skill in skills:
        key = skill.lower()
        if key in _CANONICAL_LABELS:
            by_lower[key] = _CANONICAL_LABELS[key]
        elif key not in by_lower:
            by_lower[key] = skill
    return set(by_lower.values())


def extract_required_skills(repo_path: Path) -> set[str]:
    """Repo-wide, not per issue: real issue text is prose, not a structured
    list of touched files, so narrowing "required skills" to a single issue
    would need NLP/semantic matching this project deliberately skips."""
    skills: set[str] = set()

    requirements = repo_path / "requirements.txt"
    pyproject = repo_path / "pyproject.toml"
    if requirements.exists() or pyproject.exists():
        skills.add("Python")
    if requirements.exists():
        skills.update(_read_requirements_txt(requirements))
    if pyproject.exists():
        skills.update(_read_pyproject_toml(pyproject))

    package_json = repo_path / "package.json"
    if package_json.exists():
        skills.add("JavaScript")
        skills.update(_read_package_json(package_json))
    if (repo_path / "tsconfig.json").exists():
        skills.add("TypeScript")

    if (repo_path / "Dockerfile").exists():
        skills.add("Docker")

    return _dedupe_case_insensitive(skills)


def compute_gap(required_skills: set[str], user_skills: list[str]) -> dict:
    user_normalized = {s.lower() for s in user_skills}
    have = {s for s in required_skills if s.lower() in user_normalized}
    gap = required_skills - have
    return {
        "required": sorted(required_skills),
        "have": sorted(have),
        "gap": sorted(gap),
    }
