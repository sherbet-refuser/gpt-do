from __future__ import annotations

import logging

from pydantic import BaseModel

from .action import Action

logger = logging.getLogger(__name__)


class Complete(Action["Complete.Args", "Complete.Output"]):
    """The user's request has been completely handled.

    Args:
        completed_objectives: A list of objectives that were completed.
        failed_objectives: A list of objectives that failed.
        summary: A summary of the action taken.
        tool_feedback: Feedback on the functionality of the available tools.

    Output:
        None - session ends.
    """

    confirm = False

    class Args(BaseModel):
        completed_objectives: list[str]
        failed_objectives: list[str]
        summary: str
        tool_feedback: str

    class Output(BaseModel):
        pass

    @classmethod
    def perform(cls, args: Args) -> Output:
        """No action to perform."""

        def pretty_lines(lines: list[str]) -> str:
            if lines:
                return "\n" + "\n".join(f"- {x}" for x in lines)
            return "[]"

        logger.info(
            f"[bold]Completed objectives[/]: {pretty_lines(args.completed_objectives)}"
        )
        logger.info(
            f"[bold]Failed objectives[/]: {pretty_lines(args.failed_objectives)}"
        )
        logger.info(f"[bold]Summary[/]: {args.summary}")
        logger.info(f"[bold]Tool feedback[/]: {args.tool_feedback}")
        return cls.Output()
