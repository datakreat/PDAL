EXTRACTION_PROMPT = """
You are an RF systems parameter extraction engine.

Extract engineering parameters from the text.

RULES:
- Return ONLY valid JSON
- No markdown
- No explanation
- Use ONLY canonical parameter names
- Convert units to SI

Allowed parameters:
- Pt : transmit power in W
- frequency : carrier frequency in Hz
- R : range in meters
- Gt : transmit antenna gain (linear)
- Gr : receive antenna gain (linear)
- B : bandwidth in Hz
- T : noise temperature in Kelvin
- B : bandwidth in Hz
- T : noise temperature in Kelvin

Text:
{input_text}

Return format:
{{
  "parameters": {{
    "Pt": 5,
    "frequency": 77000000000,
    "R": 2000
  }}
}}
"""