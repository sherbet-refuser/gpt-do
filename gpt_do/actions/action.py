from __future__ import annotations

import json
import logging
import textwrap
from abc import abstractmethod
from typing import Any, Protocol, Type, TypeVar

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from .. import MODEL, GptDont

logger = logging.getLogger(__name__)

ArgsT = TypeVar("ArgsT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class Action(Protocol[ArgsT, OutputT]):
    """Base class for actions."""

    Args: Type[ArgsT]
    Output: Type[OutputT]
    confirm: bool

    @classmethod
    def description(cls) -> str:
        """Return the action description."""
        doc = cls.__doc__
        assert doc is not None
        doc = textwrap.dedent(doc).strip()
        return doc

    @classmethod
    def summary(cls) -> str:
        """Return the action summary."""
        return cls.description().split("\n", maxsplit=1)[0].strip()

    @classmethod
    @abstractmethod
    def perform(cls, args: ArgsT) -> OutputT:
        """Perform the action."""

    @classmethod
    def run(cls, client: OpenAI, context: list[ChatCompletionMessageParam]) -> OutputT:
        """Run the action."""

        context.append(
            {"role": "system", "content": cls.description()},
        )
        logger.debug(context)
        if cls.Args.__fields__:
            try:
                completion = client.beta.chat.completions.parse(
                    model=MODEL,
                    messages=context,
                    response_format=cls.Args,
                )
            except openai.BadRequestError:
                logger.debug(json.dumps(cls.Args.model_json_schema()))
                raise
            logger.debug(completion)
            response = completion.choices[0].message
            if response.refusal:
                raise ValueError(f"Refusal: {response.refusal}")
            assert response.content is not None
            context.append({"role": "assistant", "content": response.content})
            args = response.parsed
            assert isinstance(args, cls.Args)
            arg_log_level = logging.INFO if cls.confirm else logging.DEBUG
            pretty_args = "\n".join(
                f"  {key} = {value}" for key, value in args.dict().items()
            )
            logger.log(arg_log_level, f"[bold]Arguments[/]:\n{pretty_args}")
        else:
            args = cls.Args()
        if cls.confirm:
            # TODO: clean this up
            # TODO: allow sending a message back instead of killing it
            user_response = input("\nProceed? [y/N] ")
            if user_response.lower() != "y":
                raise GptDont()
            print()
        output = cls.perform(args)
        context.append(
            {"role": "system", "content": f"Output: {output.model_dump_json()}"}
        )
        return output


GenericAction = type[Action[Any, Any]]
