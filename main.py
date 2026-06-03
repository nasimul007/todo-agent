from agent import TodoAgent


agent = TodoAgent()

while True:
    user_input = input(">> ")
    result = agent.think(user_input)

    print("Result:", result)
