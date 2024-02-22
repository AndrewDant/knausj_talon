from talon import Module, actions
from typing import Any
import os
from ...core.snippets.snippet_types import Snippet


mod = Module()


@mod.action_class
class Actions:
    def c_get_texts(target: Any) -> list[str]:
        """Get text for Cursorless target"""
        return actions.user.private_cursorless_command_get(
            {
                "name": "getText",
                "target": target,
            }
        )

    def c_insert_snippet(destination: Any, name: str):
        """Insert cursorless snippet <name>"""
        snippet: Snippet = actions.user.get_snippet(name)

        actions.user.cursorless_insert_snippet(
            snippet.body, destination, snippet.insertion_scopes
        )

    def c_wrap_with_snippet(target: Any, id: str):
        """Wrap the target with snippet <id>"""
        index = id.rindex(".")
        snippet_name = id[:index]
        variable_name = id[index + 1]
        snippet: Snippet = actions.user.get_snippet(snippet_name)
        variable = snippet.get_variable_strict(variable_name)

        actions.user.cursorless_wrap_with_snippet(
            snippet.body, target, variable.name, variable.wrapper_scope
        )
