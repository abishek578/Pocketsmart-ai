from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class LoginRequest(BaseModel):
    email: str
    password: str
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class HomeItemInput(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    quantity: int = Field(default=1, ge=1, le=50)

class HomeRequest(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    rooms: list[str] = Field(min_length=1, max_length=10)
    items: list[HomeItemInput] = Field(min_length=1, max_length=30)
    style: str = Field(default="modern", max_length=100)
    additional_requirements: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    guest_count: int = Field(gt=0, le=10_000)
    event_type: str = Field(min_length=2, max_length=100)
    venue_type: str = Field(default="not specified", max_length=100)
    catering_needed: bool = True
    decoration_needed: bool = True
    entertainment_needed: bool = False
    city: str = Field(default="", max_length=100)
    additional_requirements: str = Field(default="", max_length=1000)

class JewelryRequest(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    style_preferences: str = Field(default="elegant", max_length=500)
    metal_preference: str = Field(default="any", max_length=80)
    color_preference: str = Field(default="", max_length=100)
    additional_requirements: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    item_type: str
    name: str
    description: str = ""
    estimated_price: float = Field(ge=0)
    quantity: int = Field(default=1, ge=1)
    search_terms: str
    platforms: list[str] = Field(default_factory=list)
    shopping_links: dict[str, str] = Field(default_factory=dict)

class BudgetCategory(BaseModel):
    category: str
    allocation: float = Field(ge=0)
    items: list[RecommendationItem] = Field(default_factory=list)

class RecommendationResult(BaseModel):
    planner_type: Literal["home", "party", "jewelry"]
    total_budget: float = Field(ge=0)
    budget_breakdown: list[BudgetCategory] = Field(default_factory=list)
    remaining_budget: float = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)
    styling_tips: list[str] = Field(default_factory=list)
    mode: Literal["gemini", "demo"] = "gemini"
    outfit_analysis: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
