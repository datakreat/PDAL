import json
from extractor.llm import generate_response
from extractor.prompt import EXTRACTION_PROMPT


def extract_parameters(text):

    prompt = EXTRACTION_PROMPT.format(input_text=text)

    raw = generate_response(prompt)

    print("\nLLM RAW OUTPUT:")
    print(raw)

    # Robust parsing: Clean markdown json codeblocks if LLM returned them
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
        return parsed

    except Exception as e:
        print("Extraction parsing failed:", e)
        return {"family": "rf", "target": "Pt", "parameters": {}}