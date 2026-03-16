import random
import datetime

def show_help():
    print("\nYou can try the following commands:")
    print("- hello / hi")
    print("- how are you")
    print("- what is your name")
    print("- internship")
    print("- artificial intelligence")                                                                         
    print("- date")
    print("- time")
    print("- calculate 5+3")
    print("- I am sad / I am happy")
    print("- set my name Gaurav..!!")
    print("- bye\n")

def chatbot():
    user_name = None

    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    greeting_responses = [
        "Hello. How can I assist you?",
        "Hi. What would you like to know?",
        "Greetings. How may I help you?"
    ]

    print("AI Rule-Based Chatbot")
    print("Type 'help' to see available commands.")
    print("Type 'bye' to exit.\n")

    while True:
        user_input = input("You: ").lower()

        # Greeting
        if any(word in user_input for word in greetings):
            print("Bot:", random.choice(greeting_responses))

        # Name memory
        elif user_input.startswith("set my name"):
            try:
                user_name = user_input.split("set my name")[1].strip()
                print(f"Bot: Your name has been stored as {user_name}.")
            except:
                print("Bot: Please provide a valid name.")

        elif "my name" in user_input and user_name:
            print(f"Bot: Your name is {user_name}.")

        # How are you
        elif "how are you" in user_input:
            print("Bot: I am functioning as expected.")

        # Bot name
        elif "your name" in user_input:
            print("Bot: I am a rule-based chatbot developed for the AI internship.")

        # Internship
        elif "internship" in user_input:
            print("Bot: The internship focuses on building practical AI projects such as chatbots and AI games.")

        # AI explanation
        elif "artificial intelligence" in user_input or "ai" in user_input:
            print("Bot: Artificial Intelligence is the simulation of human intelligence in machines.")

        # Date
        elif "date" in user_input:
            today = datetime.date.today()
            print("Bot: Today's date is", today)

        # Time
        elif "time" in user_input:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print("Bot: Current time is", current_time)

        # Calculator
        elif user_input.startswith("calculate"):
            try:
                expression = user_input.replace("calculate", "").strip()
                result = eval(expression)
                print("Bot: The result is", result)
            except:
                print("Bot: Please enter a valid mathematical expression.")

        # Sentiment detection
        elif "sad" in user_input:
            print("Bot: I hope things improve soon. Stay positive.")

        elif "happy" in user_input:
            print("Bot: That is good to hear.")

        # Help
        elif user_input == "help":
            show_help()

        # Exit
        elif user_input == "bye":
            print("Bot: Goodbye. Have a productive day.")
            break

        # Default
        else:
            print("Bot: I do not understand that command. Type 'help' for options.")

if __name__ == "__main__":
    chatbot()
