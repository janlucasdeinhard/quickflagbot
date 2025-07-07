from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os, re

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TEST_FOLDER_PATH = os.getenv("TEST_FOLDER_PATH")

# Load DB schema context
with open("db_description.txt", "r") as f:
    db_context = f.read()
# Load further guidelines
with open("chatbot_guidelines.txt", "r") as f:
    guidelines = f.read()

# Initialize message history with system prompt (context)
messages = [
    {
        "role": "system",
        "content": f"""
You are a helpful assistant that writes SQL data quality test queries.

Use this database context for your answers:
---
{db_context}
---
In case the user suggests that he wants to deploy the test or save the test, inform him that he needs to type 'save test' to save the test to the database.

Also use these guidelines:
---
{guidelines}
---
"""
    }
]

def save_test_to_file(test_sql, description):
    # Create a safe filename
    slug = re.sub(r'\W+', '_', description.lower())[:50]
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slug}.sql"
    filepath = os.path.join(TEST_FOLDER_PATH, filename)

    with open(filepath, "w") as f:
        f.write(f"-- Test: {description}\n\n{test_sql.strip()}\n")

    print(f"✅ Test saved to {filepath}")
    return filepath

def extract_sql_from_response(text):
    # crude but effective for GPT replies
    import re
    match = re.search(r"```sql(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()  # fallback

# Chat loop
def chat():
    print("Type your data quality test request (or 'exit' to quit):\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        if "save test"==user_input.lower():
            # Assume last assistant message has the SQL
            sql_test = extract_sql_from_response(assistant_reply)
            description = user_input.strip()
            save_test_to_file(sql_test, description)

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0.2
        )

        # Extract and print reply
        assistant_reply = response.choices[0].message.content
        print(f"\nAssistant:\n{assistant_reply}\n")

        # Add assistant response to history
        messages.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    chat()
