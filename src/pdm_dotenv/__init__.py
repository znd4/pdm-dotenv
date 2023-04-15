"""
    pdm-dotenv

    A pdm plugin that automatically loads .env files
    :author: Zane Dufour <zane@znd4.me>
    :license: MIT
"""
from typing import Any
import dotenv
from pdm.project import ConfigItem, Project
from pdm.signals import pre_run
from pdm.core import Core


def load_dotenv(project: Project, **_: Any) -> None:
    dotenv_path = project.root / project.config["dotenv.path"]
    project.core.ui.echo(f"Loading dotenv file {dotenv_path}")
    dotenv.load_dotenv(dotenv_path)


def plugin(core: Core) -> None:
    core.add_config(
        "dotenv.path",
        ConfigItem("Path to your .env file", ".env", env_var="PDM_DOTENV_PATH"),
    )
    pre_run.connect(load_dotenv)
