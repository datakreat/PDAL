import json
from extractor.llm import generate_response

from extractor.prompt import EXTRACTION_PROMPT


def extract_parameters(text):

    prompt = EXTRACTION_PROMPT.format(
        input_text=text
    )

    raw = generate_response(prompt)

    print("\nLLM RAW OUTPUT:")
    print(raw)

    try:
        parsed = json.loads(raw)

        return parsed["parameters"]

    except Exception as e:

        print("Extraction failed:", e)

        return {}