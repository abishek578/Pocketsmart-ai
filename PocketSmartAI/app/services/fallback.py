from ..models.schemas import BudgetCategory, HomeRequest, JewelryRequest, PartyRequest, RecommendationItem, RecommendationResult
from .platform_links import make_search_links

def _item(item_type, name, price, search, platforms, qty=1, desc=""):
    return RecommendationItem(
        item_type=item_type, name=name, description=desc, estimated_price=price,
        quantity=qty, search_terms=search, platforms=platforms,
        shopping_links=make_search_links(search, platforms)
    )

def home_fallback(data: HomeRequest) -> RecommendationResult:
    budget = data.total_budget
    categories = []
    per = budget / max(len(data.items), 1)
    for requested in data.items:
        unit = min(max(per / requested.quantity, 700), 15000)
        price = round(unit * requested.quantity, 2)
        categories.append(BudgetCategory(
            category=requested.category, allocation=price,
            items=[_item(requested.category, f"Budget-friendly {requested.category}", unit,
                         f"{data.style} {requested.category} India",
                         ["amazon", "flipkart", "ikea"], requested.quantity,
                         "Demo fallback recommendation; verify current price on the retailer.")]
        ))
    total = min(sum(c.allocation for c in categories), budget)
    return RecommendationResult(
        planner_type="home", total_budget=budget, budget_breakdown=categories,
        remaining_budget=max(0, budget-total),
        warnings=["Gemini is unavailable, so these are demo fallback recommendations."],
        styling_tips=[f"Keep the overall room palette consistent with your {data.style} preference."],
        mode="demo"
    )

def party_fallback(data: PartyRequest) -> RecommendationResult:
    budget = data.total_budget
    enabled = []
    if data.catering_needed: enabled.append(("catering", .45, "party catering"))
    if data.venue_type: enabled.append(("venue", .25, f"{data.venue_type} venue"))
    if data.decoration_needed: enabled.append(("decoration", .20, "party decoration"))
    if data.entertainment_needed: enabled.append(("entertainment", .10, "party entertainment"))
    total_weight = sum(x[1] for x in enabled) or 1
    parts = []
    for category, weight, term in enabled:
        alloc = round(budget * weight / total_weight, 2)
        platforms = ["swiggy", "zomato"] if category == "catering" else ["amazon", "flipkart"]
        if category == "venue": platforms = ["oyo", "booking"]
        parts.append(BudgetCategory(
            category=category, allocation=alloc,
            items=[_item(category, f"Demo {category} option", alloc,
                         f"{data.event_type} {term} {data.city}", platforms,
                         desc="Demo fallback recommendation; verify availability and current price.")]
        ))
    total = sum(c.allocation for c in parts)
    return RecommendationResult(
        planner_type="party", total_budget=budget, budget_breakdown=parts,
        remaining_budget=max(0, budget-total),
        warnings=["Gemini is unavailable, so these are demo fallback recommendations."],
        styling_tips=["Reserve a small contingency amount for last-minute event expenses."],
        mode="demo"
    )

def jewelry_fallback(data: JewelryRequest) -> RecommendationResult:
    budget = data.total_budget
    options = [
        ("earrings", .25, "statement earrings"),
        ("necklace", .40, "matching necklace"),
        ("bracelet", .20, "minimal bracelet"),
        ("ring", .15, "elegant ring"),
    ]
    items = [_item(kind, f"{data.style_preferences.title()} {kind}", round(budget*weight,2),
                    f"{data.occasion} {data.style_preferences} {data.metal_preference} {term}",
                    ["amazon","flipkart","myntra"], desc="Demo fallback recommendation; verify material and price before purchase.")
             for kind, weight, term in options]
    return RecommendationResult(
        planner_type="jewelry", total_budget=budget,
        budget_breakdown=[BudgetCategory(category="jewelry", allocation=budget, items=items)],
        remaining_budget=0,
        warnings=["Gemini is unavailable, so these are demo fallback recommendations."],
        styling_tips=["Use one statement piece and keep the remaining jewelry understated for balance."],
        mode="demo"
    )
