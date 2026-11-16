import argparse
import csv
import os

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

DEFAULT_PROMPT = (
    "You are a supportive tutor. Return exactly two lines: "
    "Summary: [brief summary] and Feedback: [one constructive next step]."
)


def read_responses(path):
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or "response" not in reader.fieldnames:
            raise ValueError("Input CSV must include a 'response' column")
        return [
            {"name": row.get("name", "Student"), "response": row["response"].strip()}
            for row in reader if row.get("response", "").strip()
        ]


def review(response, prompt, dry_run=False):
    if dry_run:
        return {
            "summary": f"Offline preview: {response.strip()[:100]}",
            "feedback": "Check the key idea and add one supporting detail.",
        }

    if load_dotenv:
        load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY before running without --dry-run")

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    reply = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Student answer: {response}"},
        ], "temperature": 0.3},
        timeout=60,
    )
    reply.raise_for_status()
    text = reply.json()["choices"][0]["message"]["content"].strip()
    parts = {}
    for line in text.splitlines():
        if ":" in line:
            label, value = line.split(":", 1)
            parts[label.strip().lower()] = value.strip()
    return {
        "summary": parts.get("summary", text),
        "feedback": parts.get("feedback", "Review the answer and suggest a next step."),
    }


def main():
    parser = argparse.ArgumentParser(description="Summarise student answers and suggest feedback.")
    parser.add_argument("input", help="CSV file with name and response columns")
    parser.add_argument("-o", "--output", default="triage_output.csv")
    parser.add_argument("--dry-run", action="store_true", help="Run offline with example feedback")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Instructions sent to the LLM")
    args = parser.parse_args()

    answers = read_responses(args.input)
    with open(args.output, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["name", "response", "summary", "feedback"])
        writer.writeheader()
        for answer in answers:
            result = review(answer["response"], args.prompt, args.dry_run)
            writer.writerow({**answer, **result})
    print(f"Processed {len(answers)} answers -> {args.output}")


if __name__ == "__main__":
    main()
