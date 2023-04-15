from pdm.project import Project
from pdm.pytest import PDMCallable


def test_happy_path(project: Project, pdm: PDMCallable) -> None:
    (project.root / ".env").write_text("FOO_BAR_BAZ=hello")

    def check_env():
        pdm(
            [
                "run",
                "bash",
                "-c",
                f'echo $FOO_BAR_BAZ > {project.root / "foo.txt"}',
            ],
            obj=project,
        )

        assert (project.root / "foo.txt").read_text().strip() == "hello"

    check_env()
    check_env()


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

    def check_env():
        pdm(
            [
                "run",
                "bash",
                "-c",
                f'echo $FOO_BAR_BAZ > {project.root / "foo.txt"}',
            ],
            obj=project,
        )
        assert (project.root / "foo.txt").read_text().strip() == "hello"

    check_env()
