import os
import random
import urllib.parse
import requests


def _cloudflare_image(prompt: str):
    account_id = os.getenv("CF_ACCOUNT_ID")
    token = os.getenv("CF_API_TOKEN")
    if not account_id or not token:
        print("CF credentials not set")
        return None

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/ai/run/@cf/black-forest-labs/flux-1-schnell"
    )
    try:
        res = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"prompt": prompt, "steps": 4},
            timeout=60,
        )
        if res.status_code == 200:
            b64 = res.json().get("result", {}).get("image")
            if b64:
                return f"data:image/jpeg;base64,{b64}"
        print("Cloudflare image error:", res.status_code, res.text[:200])
    except Exception as e:
        print("Cloudflare request failed:", repr(e)[:200])
    return None


def generate_ad_image(headline: str, product_description: str) -> str:
    prompt = (
        f"professional product photography of {product_description}, "
        f"centered on a clean studio background, soft lighting, "
        f"high quality commercial advertisement, no text, no watermark"
    )

    image = _cloudflare_image(prompt)
    if image:
        return image

    seed = random.randint(1, 999999)
    encoded = urllib.parse.quote(prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=768&height=768&nologo=true&seed={seed}"
    )