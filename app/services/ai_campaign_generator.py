import os
import re
import json
import groq
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TEXT_MODEL = "qwen/qwen3.8-27b"
MAX_ATTEMPTS = 3


def _extract_json(text):
    # Qwen3 models may include reasoning in <think> tags; remove it
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in model response")
    return json.loads(text[start:end + 1])


def _clean_variants(variants):
    cleaned = []
    for i, v in enumerate(variants, start=1):
        cleaned.append({
            "id": v.get("id", i),
            "angle": str(v["angle"]),
            "headline": str(v["headline"]),
            "caption": str(v["caption"]),
            "cta": str(v["cta"]),
            "hashtags": [str(h) for h in v.get("hashtags", [])],
            "score": int(v.get("score", 80)),
            "tips": [str(t) for t in v.get("tips", [])],
        })
    if not cleaned:
        raise ValueError("Model returned no variants")
    return cleaned


def _fallback_variants(data):
    product = data.product_description.strip()
    short = product[:60]
    return [
        {
            "id": 1,
            "angle": "Benefit-first",
            "headline": f"Meet {short}",
            "caption": f"{product}. Made for {data.audience} on {data.platform}.",
            "cta": "Learn more",
            "hashtags": ["#New", "#MustHave", "#Trending"],
            "score": 75,
            "tips": ["Lead with a clear visual of the product.", "Keep the first 3 seconds punchy."],
        },
        {
            "id": 2,
            "angle": "Problem-solution",
            "headline": "The upgrade you've been waiting for",
            "caption": f"Tired of the usual? {product} changes that.",
            "cta": "See how it works",
            "hashtags": ["#Upgrade", "#Solution", "#Discover"],
            "score": 72,
            "tips": ["Open with the problem your audience feels.", "Show the product solving it."],
        },
        {
            "id": 3,
            "angle": "Offer-focused",
            "headline": "Limited-time offer inside",
            "caption": f"Get {short} while it lasts.",
            "cta": "Shop now",
            "hashtags": ["#Offer", "#LimitedTime", "#ShopNow"],
            "score": 74,
            "tips": ["Put the offer in large text early.", "Add urgency with a deadline."],
        },
    ]


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
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            parsed = _extract_json(content)
            return _clean_variants(parsed["variants"])
        except (groq.BadRequestError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            print(f"Campaign generation attempt {attempt}/{MAX_ATTEMPTS} failed: {repr(e)[:200]}")

    print("All attempts failed, using fallback variants")
    return _fallback_variants(data)