import json
from ..models.schemas import HomeRequest, PartyRequest, JewelryRequest

JSON_RULES = """
Return ONLY valid JSON. Do not use Markdown fences.
Prices are estimates in Indian Rupees (INR), not live retailer prices.
Never exceed the supplied total budget when summing item estimated_price * quantity.
Use realistic Indian-market estimates.
For each item provide a concise search_terms value suitable for a retailer search.
"""

def home_prompt(data: HomeRequest) -> str:
    return f"""
You are PocketSmart AI, a budget planning assistant for India.
Create a practical home interior shopping plan.

User input:
{json.dumps(data.model_dump(), indent=2)}

Choose sensible budget allocations for furniture, lighting, decor, and other requested items.
Recommend concrete item types, quantities, estimated prices, descriptions, and search terms.
Use Amazon, Flipkart and IKEA where appropriate.
{JSON_RULES}

Required JSON:
{{
  "planner_type": "home",
  "total_budget": {data.total_budget},
  "budget_breakdown": [
    {{
      "category": "lighting",
      "allocation": 0,
      "items": [
        {{
          "item_type": "ceiling light",
          "name": "example product type",
          "description": "...",
          "estimated_price": 0,
          "quantity": 1,
          "search_terms": "..."
        }}
      ]
    }}
  ],
  "remaining_budget": 0,
  "warnings": [],
  "styling_tips": []
}}
"""

def party_prompt(data: PartyRequest) -> str:
    return f"""
You are PocketSmart AI, a budget planning assistant for India.
Create a practical event plan.

User input:
{json.dumps(data.model_dump(), indent=2)}

Allocate the budget among venue, catering, decoration and entertainment according to what the user requested.
Consider guest count and event type. For food use Swiggy/Zomato where relevant; for accommodation or venue research use OYO/Booking when appropriate.
{JSON_RULES}

Required JSON:
{{
  "planner_type": "party",
  "total_budget": {data.total_budget},
  "budget_breakdown": [],
  "remaining_budget": 0,
  "warnings": [],
  "styling_tips": []
}}
"""

def jewelry_prompt(data: JewelryRequest, has_image: bool) -> str:
    image_note = (
        "An outfit image is attached. Analyze broad color/style cues and use them only to "
        "recommend complementary jewelry. Do not identify the person."
        if has_image else "No outfit image is attached. Use the written preferences only."
    )
    return f"""
You are PocketSmart AI, a jewelry budget planning assistant for India.

User input:
{json.dumps(data.model_dump(), indent=2)}

{image_note}
Recommend earrings, necklaces, bracelets, rings or other suitable jewelry.
Keep total estimated cost within the budget. Use Amazon and Flipkart and fashion platforms where appropriate.
If an image is attached, include a short outfit_analysis object with color/style observations.

{JSON_RULES}

Required JSON:
{{
  "planner_type": "jewelry",
  "total_budget": {data.total_budget},
  "budget_breakdown": [
    {{
      "category": "jewelry",
      "allocation": 0,
      "items": [
        {{
          "item_type": "earrings",
          "name": "...",
          "description": "...",
          "estimated_price": 0,
          "quantity": 1,
          "search_terms": "..."
        }}
      ]
    }}
  ],
  "remaining_budget": 0,
  "warnings": [],
  "styling_tips": [],
  "outfit_analysis": {{
    "colors": [],
    "style": "",
    "formality": ""
  }}
}}
"""
