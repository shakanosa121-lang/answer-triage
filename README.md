# answer-triage

A small Python command-line tool that summarises student short answers and suggests constructive feedback.

## Install

Install Python, then run:

    pip install requests python-dotenv

python-dotenv is optional; it lets the tool load OPENAI_API_KEY from a local .env file.

## Offline demo

    python answer_triage.py student_responses.csv --dry-run

This needs no API key or internet connection and writes triage_output.csv.

## Run with an API

Set OPENAI_API_KEY in your environment (or in .env if python-dotenv is installed), then run:

    python answer_triage.py student_responses.csv -o reviewed.csv

It uses the OpenAI chat completions endpoint. Set OPENAI_BASE_URL or OPENAI_MODEL to use a compatible endpoint or another model. Use --prompt "Your tutor instructions" to customize the prompt. Review AI suggestions before sharing them with students.

The input CSV needs name and response columns. Example output:

    name,response,summary,feedback
    Alex Example,"A function is reusable code that performs a task.","Offline preview: A function is reusable code that performs a task.","Check the key idea and add one supporting detail."
