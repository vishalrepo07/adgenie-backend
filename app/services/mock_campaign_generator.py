from app.schemas import AdVariant, CampaignInput


PLATFORM_TAGS = {
    "Instagram": ["#instadeals", "#newlaunch", "#shopnow"],
    "YouTube": ["#mustwatch", "#productreview", "#newtech"],
    "Facebook": ["#specialoffer", "#smallbusiness", "#discover"],
    "LinkedIn": ["#businessgrowth", "#productivity", "#innovation"],
}

ANGLE_TEMPLATES = [
    {
        "angle": "Benefit-first",
        "headline": "Make {product} work smarter for your day",
        "caption": "Built for {audience}, this offer highlights the real benefit first: less effort, better results, and a reason to act now.",
        "cta": "Try it today",
        "score": 86,
        "tips": [
            "Keep the opening line short for faster attention.",
            "Use one clear CTA instead of multiple actions.",
        ],
    },
    {
        "angle": "Problem-solution",
        "headline": "Still struggling with {problem}? Meet a better way",
        "caption": "Turn the everyday problem into a clear product story. Show the pain point, introduce the solution, then close with a confident next step.",
        "cta": "See how it helps",
        "score": 82,
        "tips": [
            "Mention the problem in the first 3 seconds of video.",
            "Add a visual before-and-after comparison.",
        ],
    },
    {
        "angle": "Offer-focused",
        "headline": "Your next upgrade starts with {product}",
        "caption": "A direct campaign angle for {platform}: simple promise, strong offer, and a CTA designed for users who are ready to compare options.",
        "cta": "Get the offer",
        "score": 79,
        "tips": [
            "Add urgency if there is a real deadline.",
            "Use the strongest product feature near the CTA.",
        ],
    },
]


def _summarize_product(description: str) -> str:
    words = [word.strip(".,!?:;") for word in description.split()]
    meaningful = [word for word in words if len(word) > 3]
    return " ".join(meaningful[:4]) or "your product"


def _problem_from_description(description: str) -> str:
    product = _summarize_product(description)
    return f"finding the right {product}"


def generate_mock_campaign(data: CampaignInput) -> list[AdVariant]:
    product = _summarize_product(data.product_description)
    problem = _problem_from_description(data.product_description)
    platform_tags = PLATFORM_TAGS.get(data.platform, ["#adgenie", "#campaign", "#shopnow"])

    variants = []
    for index, template in enumerate(ANGLE_TEMPLATES, start=1):
        hashtags = platform_tags + [f"#{data.platform.lower()}ads", f"#{data.budget.lower()}budget"]
        variants.append(
            AdVariant(
                id=index,
                angle=template["angle"],
                headline=template["headline"].format(product=product, problem=problem),
                caption=template["caption"].format(
                    audience=data.audience.lower(),
                    platform=data.platform,
                    product=product,
                    problem=problem,
                ),
                cta=template["cta"],
                hashtags=hashtags,
                score=template["score"],
                tips=template["tips"],
            )
        )

    return variants
