from pdm.cli.actions import textwrap
import _pytest
import pytest
import typing
from pdm.project import Project
from pdm.pytest import RunResult
import pathlib
import tempfile
from typing import TYPE_CHECKING, List
import toml

if TYPE_CHECKING:
    from pdm.pytest import PDMCallable


def assert_in_env(
    pdm_in_project: typing.Callable[[List[str]], RunResult],
    key: str,
    val: str,
) -> None:
    with tempfile.TemporaryDirectory() as td:
        fp = pathlib.Path(td)
        out_path = fp / "foo.txt"
        out_path.touch()
        cmd = [
            "run",
            "python",
            "-c",
            textwrap.dedent(
                f"""
                import os, pathlib
                pathlib.Path({str(out_path)!r}).write_text(os.environ.get({key!r}, ""))
                """
            ),
        ]
        pdm_in_project(cmd)

        assert val == (fp / "foo.txt").read_text().strip()


def test_build(project: Project, pdm: "PDMCallable") -> None:
    """
    pdm build should pick up and use environment variable
    e.g. PDM_BUILD_ISOLATION
    desc: Isolate the build environment from the project environment
    default: True
    """
    exp_ver = "1.2.3"
    (project.root / ".env").write_text(f"PDM_BUILD_ISOLATION=false\nVERSION={exp_ver}")
    # setup.py that includes environment variable FOO_BAR in the package
    (project.root / "setup.py").write_text(
        textwrap.dedent(
            """
            import os
            from setuptools import setup
            version = os.environ.get("VERSION", "0.0.1")
            setup(
                name="foo",
                version=version,
            )
            """
        )
    )
    pyproject_toml = toml.loads((project.root / "pyproject.toml").read_text())
    del pyproject_toml["project"]
    pyproject_toml["build-system"] = {
        "requires": ["setuptools", "wheel"],
        "build-backend": "setuptools.build_meta",
    }
    (project.root / "pyproject.toml").write_text(toml.dumps(pyproject_toml))

    pdm(
        ["build"],
        strict=True,
        obj=project,
    )
    assert (project.root / "dist" / f"foo-{exp_ver}-py3-none-any.whl").exists()


def pdm_in_project_factory(pdm: "PDMCallable", project: Project) -> RunResult:
    def wrapped(args: List[str]) -> RunResult:
        return pdm(args, strict=True, obj=project)

    return wrapped


def dotenv_set(pdm_in_project, key, val, dotenv):
    pdm_in_project(
        [
            "run",
            "dotenv",
            f"--file={dotenv}",
            "set",
            key,
            val,
        ],
    )


@pytest.mark.parametrize("quiet", (True, False))
def test_quiet(project: Project, pdm: "PDMCallable", quiet: bool) -> None:
    dotenv_set(pdm_in_project_factory(pdm, project), "foo", "bar", dotenv=project.root / ".env")

    cmd = ["run", "python", "-c", "print()"]
    if quiet:
        cmd = ["--quiet", *cmd]

    result = pdm(cmd, strict=True, obj=project)
    assert ("Loading dotenv file" in result.stdout) != quiet


ENVIRON = (("FOO_BAR_BAZ", "hello"),)


@pytest.fixture(params=[".env", "foo.env", None])
def dotenv_file(request: _pytest.fixtures.SubRequest, project: Project, pdm: "PDMCallable") -> str:
    pdm_in_project = pdm_in_project_factory(pdm, project)

    for key, val in ENVIRON:
        dotenv_set(pdm_in_project, key, val, dotenv=project.root / (request.param or ".env"))

    if request.param:
        pdm_in_project(
            [
                "config",
                "dotenv.path",
                request.param,
            ],
        )

    return request.param


def test_happy_path(dotenv_file, project: Project, pdm: "PDMCallable") -> None:
    pdm_in_project = pdm_in_project_factory(pdm, project)
    for key, val in ENVIRON:
        assert_in_env(pdm_in_project, key, val)
