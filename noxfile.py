from pathlib import Path

from nox import Session, parametrize, session

ROOT = Path(".")
REQUIREMENTS_DIR = ROOT / "requirements"


@session
def format(session: Session) -> None:
    install_requirements(session, "style")
    session.run("black", ".")
    session.run("isort", ".")


@session
def test(session: Session) -> None:
    session.notify("test_style")
    session.notify("test_types")
    session.notify("test_coverage")
    session.notify("test_suite")


@session
def test_style(session: Session) -> None:
    install_requirements(session, "style")
    session.run("black", "--check", ".")
    session.run("isort", "--check", ".")
    session.run("flake8", ".")


@session
def test_types(session: Session) -> None:
    install_requirements(session, "types")
    session.run("mypy", "--strict", "reactpy_flake8")


@session
@parametrize("flake8_version", ["3", "4", "5", "6"])
def test_suite(session: Session, flake8_version: str) -> None:
    install_requirements(session, "test-env")
    session.install(f"flake8=={flake8_version}.*")
    session.install(".")
    session.run("pytest", "tests")


@session
def test_coverage(session: Session) -> None:
    install_requirements(session, "test-env")
    session.install("-e", ".")

    posargs = session.posargs[:]

    if "--no-cov" in session.posargs:
        posargs.remove("--no-cov")
        session.log("Coverage won't be checked")
        session.install(".")
    else:
        posargs += ["--cov=reactpy_flake8", "--cov-report=term"]
        session.install("-e", ".")

    session.run("pytest", "tests", *posargs)


def install_requirements(session: Session, name: str) -> None:
    session.install("-r", str(REQUIREMENTS_DIR / f"{name}.txt"))
