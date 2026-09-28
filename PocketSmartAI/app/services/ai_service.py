import json
from typing import Any

from ..config import get_settings
from ..models.schemas import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
    RecommendationResult,
)
from .fallback import home_fallback, jewelry_fallback, party_fallback
from .platform_links import make_search_links
from .prompts import home_prompt, jewelry_prompt, party_prompt


settings = get_settings()


def _client():
    if not settings.gemini_api_key:
        return None

    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        text = (
            text.replace("```json", "", 1)
            .replace("```", "", 1)
            .strip()
        )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON object.")

    return json.loads(text[start : end + 1])


def _decorate_links(
    result: RecommendationResult,
) -> RecommendationResult:

    for category in result.budget_breakdown:
        for item in category.items:

            if not item.platforms:
                item.platforms = ["amazon", "flipkart"]

            item.shopping_links = make_search_links(
                item.search_terms,
                item.platforms,
            )

    for category in result.budget_breakdown:
        category.allocation = round(
            sum(
                item.estimated_price * item.quantity
                for item in category.items
            ),
            2,
        )

    spent = sum(
        item.estimated_price * item.quantity
        for category in result.budget_breakdown
        for item in category.items
    )

    result.remaining_budget = max(
        0,
        round(result.total_budget - spent, 2),
    )

    if spent > result.total_budget + 0.01:
        result.warnings.append(
            "Generated estimates exceed the requested budget; "
            "review quantities/prices before purchasing."
        )

    return result


def _generate(
    prompt: str,
    contents: list[Any],
) -> RecommendationResult:

    client = _client()

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    from google.genai import types

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.35,
            response_mime_type="application/json",
        ),
    )

    result = RecommendationResult.model_validate(
        _extract_json(response.text or "")
    )

    result.mode = "gemini"

    return _decorate_links(result)


def generate_home(
    data: HomeRequest,
) -> RecommendationResult:

    prompt = home_prompt(data)

    try:
        return _generate(
            prompt,
            [prompt],
        )

    except Exception as exc:
        print(
            f"GEMINI HOME ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        return home_fallback(data)


def generate_party(
    data: PartyRequest,
) -> RecommendationResult:

    prompt = party_prompt(data)

    try:
        return _generate(
            prompt,
            [prompt],
        )

    except Exception as exc:
        print(
            f"GEMINI PARTY ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        return party_fallback(data)


def generate_jewelry(
    data: JewelryRequest,
    image_bytes: bytes | None,
    mime_type: str | None,
) -> RecommendationResult:

    prompt = jewelry_prompt(
        data,
        bool(image_bytes),
    )

    try:
        contents: list[Any] = [prompt]

        if image_bytes and mime_type:
            from google.genai import types

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
            )

        return _generate(
            prompt,
            contents,
        )

    except Exception as exc:
        print(
            f"GEMINI JEWELRY ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        return jewelry_fallback(data)