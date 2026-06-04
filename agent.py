import json
import os
from typing import Any

from ollama import chat
from openai import OpenAI

from services.todo_service import TodoService


API_KEY = os.getenv("GEMINI_API_KEY")


def create_todo(title: str, description: str = "", priority: int = 3) -> str:
    """
    Create a todo item.

    Args:
        title: Todo title.
        description: Optional todo description.
        priority: Priority from 1 to 5.

    Returns:
        A confirmation message.
    """
    todo_id = TodoService.create_todo(
        title=title,
        description=description,
        priority=int(priority),
    )

    return f"Todo created with id {todo_id}"


def list_todos() -> str:
    """
    List all todo items.

    Returns:
        A string containing all todo items.
    """
    todos = TodoService.get_all_todos()

    if not todos:
        return "No todos found"

    return str(todos)


def get_todo(todo_id: int) -> str:
    """
    Get one todo item by id.

    Args:
        todo_id: Todo id.

    Returns:
        The todo item, or a not-found message.
    """
    todo = TodoService.get_todo(int(todo_id))

    return str(todo) if todo else "Todo not found"


def update_todo(
    todo_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: int | None = None,
) -> str:
    """
    Update an existing todo item.

    Args:
        todo_id: Todo id.
        title: New title.
        description: New description.
        status: New status, such as pending or completed.
        priority: New priority from 1 to 5.

    Returns:
        A confirmation message, or a not-found message.
    """
    fields = {}

    if title is not None:
        fields["title"] = title
    if description is not None:
        fields["description"] = description
    if status is not None:
        fields["status"] = status
    if priority is not None:
        fields["priority"] = int(priority)

    if not fields:
        return "No fields provided to update"

    updated = TodoService.update_todo(int(todo_id), **fields)

    return "Todo updated" if updated else "Todo not found"


def delete_todo(todo_id: int) -> str:
    """
    Delete a todo item by id.

    Args:
        todo_id: Todo id.

    Returns:
        A confirmation message, or a not-found message.
    """
    deleted = TodoService.delete_todo(int(todo_id))

    return "Todo deleted" if deleted else "Todo not found"


TOOLS = [
    create_todo,
    list_todos,
    get_todo,
    update_todo,
    delete_todo,
]

AVAILABLE_FUNCTIONS = {
    "create_todo": create_todo,
    "list_todos": list_todos,
    "get_todo": get_todo,
    "update_todo": update_todo,
    "delete_todo": delete_todo,
}


def _parse_text_tool_calls(content: str | None) -> list[dict[str, Any]]:
    if not content:
        return []

    content = content.strip()
    json_start_positions = [
        position
        for position in (content.find("["), content.find("{"))
        if position != -1
    ]

    if not json_start_positions:
        return []

    start = min(json_start_positions)
    end = max(content.rfind("]"), content.rfind("}"))

    if end == -1 or end < start:
        return []

    try:
        parsed = json.loads(content[start:end + 1])
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list):
        return []

    tool_calls = []

    for item in parsed:
        if not isinstance(item, dict):
            continue

        function_name = (
            item.get("name")
            or item.get("tool")
            or item.get("function")
            or _action_to_function_name(item.get("action"))
        )
        arguments = item.get("arguments") or item.get("args") or {}

        if function_name in AVAILABLE_FUNCTIONS and isinstance(arguments, dict):
            tool_calls.append(
                {
                    "name": function_name,
                    "arguments": arguments,
                }
            )

    return tool_calls


def _action_to_function_name(action: str | None) -> str | None:
    if not action:
        return None

    return {
        "CREATE_TODO": "create_todo",
        "LIST_TODOS": "list_todos",
        "GET_TODO": "get_todo",
        "UPDATE_TODO": "update_todo",
        "DELETE_TODO": "delete_todo",
    }.get(action.upper())


def _get_tool_calls(message) -> list[dict[str, Any]]:
    if message.tool_calls:
        return [
            {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            }
            for tool_call in message.tool_calls
        ]

    return _parse_text_tool_calls(message.content)


class TodoAgent:

    def think(self, user_input: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful todo assistant. Use tools when the "
                    "user wants to create, read, update, or delete todos."
                ),
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]

        # response = chat(
        #     model=MODEL,
        #     messages=messages,
        #     tools=TOOLS,
        # )

        client = OpenAI(
            # This is the default and can be omitted
    
            api_key = API_KEY,
            base_url = os.getenv("GOOGLE_API_URL")
        )

        completion = client.chat.completions.parse(
            model=os.getenv("LLM_MODEL"),
            messages=messages,
        )

        print(completion.choices[0].message.content)

        tool_calls = _get_tool_calls(response.message)

        if not tool_calls:
            return response.message.content

        if response.message.tool_calls:
            messages.append(response.message)

        for tool_call in tool_calls:
            function_name = tool_call["name"]
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

            if function_to_call is None:
                result = f"Unknown tool: {function_name}"
            else:
                result = function_to_call(**tool_call["arguments"])

            messages.append(
                {
                    "role": "tool",
                    "tool_name": function_name,
                    "content": str(result),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": (
                    "Answer my original request using the tool result. Do not "
                    "include tool call JSON or raw function-call labels."
                ),
            }
        )

        final_response = chat(
            model=os.getenv("LLM_MODEL"),
            messages=messages,
        )

        return final_response.message.content
