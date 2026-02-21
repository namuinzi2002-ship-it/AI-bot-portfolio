import os
import csv
from datetime import datetime
from openai import OpenAI

client = OpenAI()  # needs OPENAI_API_KEY in environment

CSV_FILE = "tasks.csv"

SYSTEM_PROMPT = """You are an assistant that helps turn messy task requests into structured tracker entries.
Return ONLY valid JSON with keys: summary, category, priority.
Category must be one of: Bug, Feature, Billing, Sales, Ops, Personal, Other.
Priority must be one of: Low, Medium, High.
Summary must be <= 12 words.
"""

def ensure_header(path: str):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "task", "summary", "category", "priority"])

def main():
    task = input("Paste task description: ").strip()
    if not task:
        print("❌ No task provided.")
        return

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()

        # minimal JSON parsing without extra dependencies
        import json
        data = json.loads(content)

        summary = data["summary"]
        category = data["category"]
        priority = data["priority"]

    except Exception as e:
        print(f"❌ Error calling AI or parsing response: {e}")
        return

    ensure_header(CSV_FILE)

    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, task, summary, category, priority])

    print("✅ Task processed and saved to tasks.csv")
    print(f"→ Summary: {summary} | {category} | {priority}")

if __name__ == "__main__":
    main()
