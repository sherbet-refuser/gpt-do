from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel

from .action import Action, GenericAction
from .add_to_calendar import AddToCalendar
from .ask_user import AskUser
from .check_date_time import CheckDateTime
from .check_location import CheckLocation
from .complete import Complete
from .display_to_user import DisplayToUser
from .execute_bash_command import ExecuteBashCommand
from .list_directory import ListDirectory
from .load_web_page import LoadWebPage
from .read_file import ReadFile

# from .search_duck_duck_go import SearchDuckDuckGo
# from .search_wikipedia import SearchWikipedia

logger = logging.getLogger(__name__)


class ActionEnum(Enum):
    DISPLAY_TO_USER = DisplayToUser.summary()
    ASK_USER = AskUser.summary()
    READ_FILE = ReadFile.summary()
    LIST_DIRECTORY = ListDirectory.summary()
    ADD_TO_CALENDAR = AddToCalendar.summary()
    CHECK_DATE_TIME = CheckDateTime.summary()
    CHECK_LOCATION = CheckLocation.summary()
    LOAD_WEB_PAGE = LoadWebPage.summary()
    # SEARCH_WIKIPEDIA = SearchWikipedia.summary()
    # SEARCH_DUCK_DUCK_GO = SearchDuckDuckGo.summary()
    EXECUTE_BASH_COMMAND = ExecuteBashCommand.summary()

    COMPLETE = Complete.summary()
    # TODO:
    # send email
    # perform advanced reasoning
    # send text
    # actual search
    # brainstorm (propose ideas, criticize, repeat)

    @classmethod
    def list(cls) -> str:
        """Return a list of action descriptions."""
        return "\n".join(f"- {action.name}: {action.value}" for action in cls)

    @classmethod
    def validate(cls) -> None:
        """Verify all the variants have an associated action."""
        for action in cls:
            action.to_action()

    def to_action(self) -> GenericAction:
        """Return the action class."""
        match self:
            case ActionEnum.READ_FILE:
                return ReadFile
            case ActionEnum.COMPLETE:
                return Complete
            case ActionEnum.DISPLAY_TO_USER:
                return DisplayToUser
            case ActionEnum.LOAD_WEB_PAGE:
                return LoadWebPage
            case ActionEnum.LIST_DIRECTORY:
                return ListDirectory
            case ActionEnum.ADD_TO_CALENDAR:
                return AddToCalendar
            case ActionEnum.CHECK_DATE_TIME:
                return CheckDateTime
            case ActionEnum.ASK_USER:
                return AskUser
            case ActionEnum.CHECK_LOCATION:
                return CheckLocation
            # case ActionEnum.SEARCH_WIKIPEDIA:
            #     return SearchWikipedia
            # case ActionEnum.SEARCH_DUCK_DUCK_GO:
            #     return SearchDuckDuckGo
            case ActionEnum.EXECUTE_BASH_COMMAND:
                return ExecuteBashCommand
            case _:
                raise NotImplementedError(f"Action not implemented: {self}")


class Choose(Action["Choose.Args", "Choose.Output"]):
    """Reason about the user's request and select the next action to perform.

    Your reasoning is private and will only be visible to you.
    If the user requested a message, you must display it to the user
    using the appropriate action.

    Actions will be confirmed by the user as appropriate before proceeding.

    Args:
        reasoning: Your reasoning about the user's request.
        current_plan: A list of steps to complete the user's request.
        action: The action to perform.

    Output:
        action: The action to perform.
    """

    confirm = False

    class Args(BaseModel):
        reasoning: str
        current_plan: list[str]
        action: ActionEnum

    class Output(BaseModel):
        action: ActionEnum

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""
        logger.info(f"[bold]Reasoning[/]: {args.reasoning}")
        pretty_plan = "\n".join(f"- {x}" for x in args.current_plan)
        logger.info(f"[bold]Current plan[/]:\n{pretty_plan}")
        return cls.Output(action=args.action)
