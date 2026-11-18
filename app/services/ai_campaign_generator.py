import os
import re
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TEXT_MODEL = "qwen/qwen3.8-27b"


def _extract_json(text):
    # Qwen3 models may include reasoning in <think> tags; remove it
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in model response")
    return json.loads(text[start:end + 1])


def generate_ai_campaign(data):
    prompt = f"""You are an expert ad copywriter. Generate 3 distinct ad variants for this product.

Product description: {data.product_description}
Platform: {data.platform}
Target audience: {data.audience}
Budget: {data.budget}

For each variant, provide a different angle (e.g. Benefit-first, Problem-solution, Offer-focused).

Respond ONLY with valid JSON in this exact structure, no other text:
{{
  "variants": [
    {{
      "id": 1,
      "angle": "string",
      "headline": "string",
      "caption": "string",
      "cta": "string",
      "hashtags": ["string", "string", "string"],
      "score": 85,
      "tips": ["string", "string"]
    }}
  ]
}}
"""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    parsed = _extract_json(content)
    return parsed["variants"]