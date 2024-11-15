from __future__ import annotations

import datetime as dt
import logging
from typing import Any, Optional

import click
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from rich import print as rprint
from rich.logging import RichHandler

from . import LOG_DIR
from .actions import Action, ActionEnum, Choose, Complete

logger = logging.getLogger("gpt_do")


def init_logging(verbosity: int, quiet: int) -> None:
    """
    Initialize console logging just for the gpt_do package using rich.

    Args:
        verbosity (int): Number of times the verbose flag `-v` is used.
        quiet (int): Number of times the quiet flag `-q` is used.
    """
    # Define logging levels from least to most verbose
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    base_index = 2  # INFO level

    # Corrected: Calculate new index based on verbosity and quietness
    new_index = base_index + verbosity - quiet

    # Clamp the index to valid range
    new_index = max(0, min(new_index, len(levels) - 1))
    level = levels[new_index]

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Set to lowest level to allow handlers to filter

    # Remove all existing handlers to prevent duplicate logs
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configure RichHandler for console output
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_path=False,
        # TODO: dim
    )
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(fmt="%(message)s")
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # Configure FileHandler for logging to a file
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"gpt_do_{timestamp}.log"
    file_handler = logging.FileHandler(filename=LOG_DIR / file_name, mode="w")
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG level to file
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)

    level_name = logging.getLevelName(level)
    logger.debug(f"Console log level: {level_name}")
    logger.debug("File log level: DEBUG")


@click.command()
@click.option(
    "--api-key",
    help="Your OpenAI API key.",
    envvar="OPENAI_API_KEY",
    required=True,
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity. Can be used multiple times.",
)
@click.option(
    "-q",
    "--quiet",
    count=True,
    help="Decrease verbosity. Can be used multiple times.",
)
def cli(
    api_key: Optional[str],
    verbose: int,
    quiet: int,
) -> None:
    """
    Command-line interface for the gpt_do tool.

    Args:
        api_key (Optional[str]): OpenAI API key.
        verbose (int): Verbosity level (number of `-v` flags).
        quiet (int): Quietness level (number of `-q` flags).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    init_logging(verbosity=verbose, quiet=quiet)

    client = OpenAI(api_key=api_key)
    system_lines = [
        "You are an agent autonomously executing a task.",
        "You will have the ability to execute a sequence of actions.",
        "You must fully fulfill the user's request.",
        "Do not hallucinate any details.",
        "You have access to the following tools:",
        ActionEnum.list(),
        f"The current date and time is {dt.datetime.now().isoformat()}.",
        "The user is in the Pacific time zone",
    ]
    history: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "\n".join(system_lines)},
    ]

    ActionEnum.validate()

    # TODO: build (and confirm) objectives?

    rprint("[bold]User Request[/]")
    user_request = input()
    print()
    # pylint: disable=line-too-long
    # user_request = (
    #     f"can you read this file for me and let me know what it does? {__file__}"
    # )
    # user_request = (
    #     f"is this file using the api correctly? {__file__} "
    #     "(API: https://platform.openai.com/docs/guides/structured-outputs)"
    # )
    # user_request = (
    #     "can you load this web page for me? "
    #     "https://platform.openai.com/docs/guides/structured-outputs"
    # )
    # user_request = (
    #     "check for files that are missing `from __future__ import annotations` "
    #     "in ./gpt_do/"
    # )
    # user_request = "add a placeholder for my birthday party next friday to my calendar"
    # user_request = (
    #     "add the event from this page to my calendar: "
    #     "https://docs.google.com/forms/d/e/1FAIpQLSdEAmP0HKukCwP-dvHFBNK5gw6OdeJkcJ_flWDVozF4NKCCGg/viewform"
    # )
    # pylint: enable=line-too-long
    history.append({"role": "user", "content": user_request})

    while True:
        # select action
        select_output: Choose.Output = Choose.run(client, history)
        # perform action
        action: type[Action[Any, Any]] = select_output.action.to_action()
        logger.info(f"[bold]Action[/]: {action.__name__} - {action.summary()}")
        action.run(client, history)
        # check if done
        if action == Complete:
            # TODO: allow denying the completion
            break
        # TODO: summarize context


if __name__ == "__main__":
    cli.main()
