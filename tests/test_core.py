from pdm.cli.actions import textwrap
from pdm.project import Project
from typing import TYPE_CHECKING
import toml

if TYPE_CHECKING:
    from pdm.pytest import PDMCallable


def check_env(project: Project, pdm: "PDMCallable") -> None:
    result = pdm(
        [
            "run",
            "python",
            "-c",
            textwrap.dedent(
                f"""
                import pathlib, os
                (
                    pathlib.Path({str(project.root)!r}) / "foo.txt"
                ).write_text(os.environ["FOO_BAR_BAZ"])
                """
            ),
        ],
        strict=True,
        obj=project,
    )

    assert (project.root / "foo.txt").read_text().strip() == "hello", result.outputs


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
    (project.root / ".env").write_text("FOO_BAR_BAZ=hello")

    check_env(project, pdm)
    check_env(project, pdm)


def test_different_file(project: Project, pdm: "PDMCallable") -> None:
    (project.root / ".foo.env").write_text("FOO_BAR_BAZ=hello")
    pdm(
        [
            "config",
            "dotenv.path",
            ".foo.env",
        ],
        obj=project,
    )

    check_env(project, pdm)
