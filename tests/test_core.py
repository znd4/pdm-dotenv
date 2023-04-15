from pdm.cli.actions import textwrap
from pdm.project import Project
from pdm.pytest import PDMCallable


def check_env(project: Project, pdm: PDMCallable) -> None:
    result = pdm(
        [
            "run",
            "python",
            "-c",
            textwrap.dedent(
                f"""
                import pathlib, os
                (
                    pathlib.Path({repr(str(project.root))}) / "foo.txt"
                ).write_text(os.environ["FOO_BAR_BAZ"])
                """
            ),
        ],
        obj=project,
    )

    assert (project.root / "foo.txt").read_text().strip() == "hello", result.outputs


def test_happy_path(project: Project, pdm: PDMCallable) -> None:
    (project.root / ".env").write_text("FOO_BAR_BAZ=hello")

    check_env(project, pdm)
    check_env(project, pdm)


def test_different_file(project: Project, pdm: PDMCallable) -> None:
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
