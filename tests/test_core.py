from pdm.cli.actions import textwrap
from pdm.project import Project
import pathlib
import tempfile
from typing import TYPE_CHECKING, Tuple, List
import toml

if TYPE_CHECKING:
    from pdm.pytest import PDMCallable


def dotenv_set(file: pathlib.Path, key: str, val: str) -> List[str]:
    return [
        "run",
        "dotenv",
        f"--file={file}",
        "set",
        key,
        val,
    ]


def check_env(project: Project, pdm: "PDMCallable", environ: Tuple[Tuple[str, str]]) -> None:
    for key, val in environ:
        with tempfile.TemporaryDirectory() as td:
            fp = pathlib.Path(td) / "foo.txt"
            pdm(
                [
                    "run",
                    "python",
                    "-c",
                    textwrap.dedent(
                        f"""
                        import os, pathlib
                        pathlib.Path({fp.name!r}).write_text(os.environ.get({key!r}, ""))
                        """
                    ),
                ],
                strict=True,
                obj=project,
            )
            assert val == fp.read_text().strip()


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


def test_happy_path(project: Project, pdm: "PDMCallable") -> None:
    environ = (("FOO_BAR_BAZ", "hello"),)
    for key, val in environ:
        pdm(
            dotenv_set(project.root / ".env", key, val),
            obj=project,
            strict=True,
        )

    check_env(project, pdm, environ)


def test_different_file(project: Project, pdm: "PDMCallable") -> None:
    environ = (("FOO_BAR_BAZ", "hello"),)
    for key, val in environ:
        pdm(
            dotenv_set(project.root / ".foo.env", key, val),
            obj=project,
            strict=True,
        )
    pdm(
        [
            "config",
            "dotenv.path",
            ".foo.env",
        ],
        obj=project,
    )

    check_env(project, pdm, environ)
