import os

import nox

os.environ.update(PDM_IGNORE_SAVED_PYTHON="1", PDM_USE_VENV="1")

PYTHON_VERSIONS = ("3.10", "3.11")


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    _test(session, cov=False)


@nox.session(python=PYTHON_VERSIONS)
def cov(session):
    _test(session, cov=True)


def _test(session: nox.Session, *, cov: bool) -> None:
    session.run("pdm", "install", "-Gtest", external=True)

    session.run("pytest", *(["--cov=src"] if cov else []), "tests/", *session.posargs)
