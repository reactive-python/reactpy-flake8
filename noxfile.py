from pathlib import Path

from nox import Session, session

ROOT = Path(".")
REQUIREMENTS_DIR = ROOT / "requirements"


@session
def test(session: Session) -> None:
    session.notify("test_style")
    session.notify("test_types")
    session.notify("test_coverage")
    session.notify("test_suite")


@session
def test_style(session: Session) -> None:
    install_requirements(session, "style")
    session.run("isort", "--check", ".")
    session.run("flake8", ".")


@session
def test_types(session: Session) -> None:
    install_requirements(session, "types")
    session.run("mypy", "--strict", "flake8_idom_hooks")


@session
def test_suite(session: Session) -> None:
    install_requirements(session, "test-env")
    session.install(".")
    session.run("pytest", "tests")


@session
def test_coverage(session: Session) -> None:
    install_requirements(session, "test-env")
    session.install("-e", ".")
    session.run("pytest", "tests", "--cov=flake8_idom_hooks", "--cov-report=term")


def install_requirements(session: Session, name: str) -> None:
    session.install("-r", str(REQUIREMENTS_DIR / f"{name}.txt"))
