from ollama import chat
from ollama import ChatResponse


def test_ollama():
    
    response: ChatResponse = chat(model='phi4-mini:latest', messages=[
    {
        'role': 'user',
        'content': 'Todays current weather of dhaka?',
    },
    ])
    print(response['message']['content'])
    