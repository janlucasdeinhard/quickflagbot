from openai import OpenAI
from dotenv import load_dotenv
import sqlglot
from sqlglot.errors import ParseError
import os
import re
import subprocess


class SQLDataQualityChatbot:
    """A chatbot that generates SQL data quality tests using OpenAI's GPT model."""

    def __init__(
        self, api_key=None, test_folder_path=None, model="gpt-4", temperature=0.2
    ):
        """
        Initialize the chatbot with configuration.

        Args:
            api_key: OpenAI API key. If None, loads from environment.
            test_folder_path: Path to save test files. If None, loads from environment.
            model: OpenAI model to use for chat completions.
            temperature: Temperature setting for the model.
        """
        # Load environment variables
        load_dotenv()

        # Initialize OpenAI client
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

        # Configuration
        self.test_folder_path = test_folder_path or os.getenv("TEST_FOLDER_PATH")
        self.model = model
        self.temperature = temperature

        # Load context files
        self.db_context = self._load_file("db_description.txt")
        self.guidelines = self._load_file("chatbot_guidelines.txt")

        # SQL extraction command template
        self.extract_command = """
            Please take the following chat history which is ordered by time of occurrence and extract the SQL test command which you think
            the user most likely want to deploy. Return only this SQL in plain text without any surrounding text. The chat history is as follows: {0}
        """

        # State variables
        self.last_sql_candidate = ""

        # Initialize conversation
        self.reset_conversation()

    def _load_file(self, filename):
        """Load content from a file."""
        try:
            with open(filename, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using empty content.")
            return ""

    def reset_conversation(self):
        """Reset the conversation history to initial state."""
        self.messages = [
            {
                "role": "system",
                "content": f"""

                    You are an expert data quality assistant.
                    Follow these guidelines:
                    ---
                    {self.guidelines}
                    ---
                    Use this database context for your answers:
                    ---
                    {self.db_context}
                    ---
                    """,
            }
        ]
        self.last_assistant_reply = ""

    #def save_test_to_file(self, test_sql, description):
    #    """Save a SQL test to a file with timestamp."""
    #    if not self.test_folder_path:
    #        raise ValueError("TEST_FOLDER_PATH not configured")
    #
    #    # Create directory if it doesn't exist
    #    os.makedirs(self.test_folder_path, exist_ok=True)
    #
    #    # Create a safe filename
    #    slug = re.sub(r"\W+", "_", description.lower())[:50]
    #    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slug}.sql"
    #    filepath = os.path.join(self.test_folder_path, filename)
    #
    #    with open(filepath, "w") as f:
    #        f.write(f"-- Test: {description}\n\n{test_sql.strip()}\n")
    #
    #    print(f"✅ Test saved to {filepath}")
    #    return filepath

    def save_test_to_file(self, sql: str, rule_name: str) -> str:
        filepath = f'tests/generated/{rule_name}.sql'
        with open(filepath, "w") as f:
            f.write(sql)
        subprocess.run(['python','run_all_tests_scheduled.py'])
        return filepath

    def extract_sql_from_response(self, text):
        """Extract SQL code from a GPT response."""
        match = re.search(r"```sql(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()  # fallback

    def send_message(self, user_input):
        """
        Send a message to the chatbot and get a response.

        Args:
            user_input: The user's message

        Returns:
            The assistant's response
        """
        # Handle save test command
        if user_input.lower() == "save test":
            sql_candidate = self.send_message(
                self.extract_command.format(self.messages)
            )
            try:
                sqlglot.parse_one(sql_candidate)
                #filepath = self.save_test_to_file(sql_candidate, "save test")
                #return f"Test saved to {filepath}"
                self.last_sql_candidate = sql_candidate
                return "__ASK_RULE_NAME__"
            except ParseError:
                return "No previous test to save. Please generate a test first."

        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})

        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
        )

        # Extract reply
        assistant_reply = response.choices[0].message.content
        self.last_assistant_reply = assistant_reply

        # Add assistant response to history
        self.messages.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    def chat_loop(self):
        """Start an interactive chat loop."""
        print("Type your data quality test request (or 'exit' to quit):\n")

        while True:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            try:
                response = self.send_message(user_input)
                print(f"\nAssistant:\n{response}\n")
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function to run the chatbot."""
    chatbot = SQLDataQualityChatbot()
    chatbot.chat_loop()


if __name__ == "__main__":
    main()
