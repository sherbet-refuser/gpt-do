from __future__ import annotations

from pydantic import BaseModel
from rich import print as rprint

from .action import Action


class AskUser(Action["AskUser.Args", "AskUser.Output"]):
    """Ask the user clarifying for clarifying information or general knowledge.

    Args:
        question: The message to display to the user.

    Output:
        user_response: The user's response.
    """

    confirm = False

    class Args(BaseModel):
        question: str

    class Output(BaseModel):
        user_response: str

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        # TODO: print helper
        question = args.question.replace(r"\\\\", r"\\")
        rprint(f"Question: {question}\n")
        answer = input("Answer: ")
        print()
        return cls.Output(user_response=answer)
