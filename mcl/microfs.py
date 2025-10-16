import ast
import logging
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .machine import Board

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MicroFS:
    def __init__(self, board: "Board") -> None:
        self.__board: "Board" = board
        self.__board.add_import("os")

    def ls(self, path: str = "/") -> list[str]:
        logger.debug(f"Listing contents of '{path}'")
        if not path.endswith("/"):
            path += "/"
        command = f"print(['{path}' + f for f in os.listdir('{path}')])"
        result_str = self.__board.execute(command)
        try:
            return ast.literal_eval(result_str)
        except (ValueError, SyntaxError):
            logger.error(f"Could not parse 'ls' output: {result_str}")
            return []

    def mkdir(self, path: str) -> None:
        logger.debug(f"Creating directory '{path}'")
        command = f"os.mkdir('{path}')"
        _ = self.__board.execute(command)

    def rm(self, path: str) -> None:
        logger.debug(f"Removing '{path}'")
        command = f"os.remove('{path}')"
        _ = self.__board.execute(command)

    def read_text(self, remote_path: str) -> str:
        logger.debug(f"Reading text file: '{remote_path}'")
        command = f"""
            with open('{remote_path}', 'r') as f:
                data = f.read()
                print(data)
        """
        command = textwrap.dedent(command)
        res = self.__board.execute_multiline(command)

        return self.__board.clean_repl_output(res)

    def write_text(self, remote_path: str, text: str) -> None:
        logger.debug(f"Writing {len(text)} chars to '{remote_path}'")
        command = f"""
            with open('{remote_path}', 'w') as f:
                _ = f.write('{text}')
        """
        command = textwrap.dedent(command)
        _ = self.__board.execute_multiline(command)
