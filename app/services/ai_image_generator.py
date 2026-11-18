import urllib.parse
import random


def generate_ad_image(headline: str, product_description: str) -> str:
    prompt = (
        f"professional advertisement product photo, {product_description}, "
        f"theme: {headline}, modern minimal style, high quality, social media ad"
    )
    encoded_prompt = urllib.parse.quote(prompt)
    seed = random.randint(1, 999999)
    return (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=768&height=768&nologo=true&seed={seed}"
    )