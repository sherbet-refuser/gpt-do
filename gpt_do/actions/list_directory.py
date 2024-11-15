from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .action import Action


class ListDirectory(Action["ListDirectory.Args", "ListDirectory.Output"]):
    """List the items in a directory.

    The output has a maximum of 100 items.

    Args:
        path: The path to the directory to list items for.
        recursive: Whether to list the directory recursively.
        extension: An optional file extension filter (including the leading '.').
        include_hidden: Whether to include hidden files.

    Output:
        files: A list of files.
        dirs: A list of directories.
        error: An error message.
    """

    confirm = False

    ITEM_LIMIT = 100

    class Args(BaseModel):
        path: str
        recursive: bool
        extension: Optional[str]
        include_hidden: bool

    class Output(BaseModel):
        files: list[str]
        dirs: list[str]
        error: Optional[str]

    @classmethod
    def perform(cls, args: Args) -> Output:
        """Execute the action."""

        path = Path(args.path)
        if not Path.exists(path):
            return cls.Output(error=f"Path not found: {path}", files=[], dirs=[])
        if not Path.is_dir(path):
            return cls.Output(
                error=f"Path is not a directory: {path}", files=[], dirs=[]
            )

        dirs_to_check = [path]

        files = []
        dirs = []

        while dirs_to_check:
            current_dir = dirs_to_check.pop()
            for item in current_dir.iterdir():
                if not args.include_hidden and item.name.startswith("."):
                    continue
                if item.is_dir():
                    dirs.append(str(item))
                    if args.recursive:
                        dirs_to_check.append(item)
                elif item.is_file():
                    if args.extension and not item.suffix == args.extension:
                        continue
                    files.append(str(item))
                if len(files) + len(dirs) >= cls.ITEM_LIMIT:
                    return cls.Output(
                        error=f"Too many items to list (limit: {cls.ITEM_LIMIT})",
                        files=files,
                        dirs=dirs,
                    )

        return cls.Output(files=files, dirs=dirs, error=None)
