"""
toy_oracle_target.py

A local "chatbot" that holds a secret and will only answer yes/no questions.
This simulates a vulnerable LLM chatbot that leaks information through
boolean responses without ever outputting the secret directly.

Run this locally on your Mac - no network, no real target.
Purpose: learning binary oracle attack mechanics.
"""

class ToyOracleChatbot:
    """
    Simulates a chatbot that has access to a secret but refuses to
    output it directly. It WILL, however, answer yes/no questions
    about the secret truthfully.

    This is the vulnerable behavior a real oracle attack exploits.
    """

    def __init__(self, secret: str):
        self._secret = secret
        self.query_count = 0

    def direct_question(self, question: str) -> str:
        """Simulates the chatbot refusing direct data requests."""
        self.query_count += 1
        return "I can't share that information directly."

    def yes_no_question(self, predicate_fn) -> bool:
        """
        Answers a yes/no question about the secret.

        In a real attack, you'd phrase this in natural language:
          "Is the first character of the password less than 'm'?"

        Here we simulate it with a Python function that returns
        True or False when evaluated against the secret.
        """
        self.query_count += 1
        return predicate_fn(self._secret)


if __name__ == "__main__":
    # Try it manually first to see how it behaves
    bot = ToyOracleChatbot(secret="hello42")

    # Direct request - refused
    print("Asking directly:", bot.direct_question("What is the secret?"))

    # Yes/no questions - answered
    print("Is length > 5?", bot.yes_no_question(lambda s: len(s) > 5))
    print("Does it start with 'h'?", bot.yes_no_question(lambda s: s[0] == 'h'))
    print("Is second char 'e'?", bot.yes_no_question(lambda s: s[1] == 'e'))

    print(f"\nTotal queries used: {bot.query_count}")
