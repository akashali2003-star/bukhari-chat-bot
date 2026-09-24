from src.agent import BasicAgent


def main() -> None:
    agent = BasicAgent(name="Assistant")
    print("Agent ready. Type 'exit' to quit.")

    while True:
        user_input = input("You> ")
        if user_input.strip().lower() in {"exit", "quit", "bye"}:
            print("Agent> Goodbye.")
            break

        response = agent.respond(user_input)
        print(f"Agent> {response}")


if __name__ == "__main__":
    main()
