from ollama import chat
from ollama import ChatResponse
import json
from services.todo_service import TodoService


SYSTEM_PROMPT = """
You are a Todo Agent.

Return ONLY valid JSON.

Available actions:

CREATE_TODO
LIST_TODOS
UPDATE_TODO
DELETE_TODO

CREATE_SCHEDULE
UPDATE_SCHEDULE
DELETE_SCHEDULE
LIST_SCHEDULES

Examples:

User: buy milk

{
  "action": "CREATE_TODO",
  "title": "buy milk"
}

User: show all todos

{
  "action": "LIST_TODOS"
}

User: schedule gym tomorrow from 5 PM to 7 PM

{
  "action": "CREATE_SCHEDULE",
  "title": "gym",
  "start_time": "tomorrow 5 PM",
  "end_time": "tomorrow 7 PM"
}

User: show schedules

{
  "action": "LIST_SCHEDULES"
}
"""


def create_todo_tool(title, description=""):
    todo_id = TodoService.create_todo(
        title=title,
        description=description
    )

    return f"Todo created with id {todo_id}"

def get_all_todos_tool():
    todos = TodoService.get_all_todos()

    return str(todos)

def delete_todo_tool(todo_id):
    TodoService.delete_todo(todo_id)

    return "Todo deleted"

class TodoAgent:

    def think(self, user_input):

        prompt = f"""{SYSTEM_PROMPT}
        User:
        {user_input}
        """

        response = chat(
            model="phi4-mini:latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]
    