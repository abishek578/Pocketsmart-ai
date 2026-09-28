from urllib.parse import quote_plus

PLATFORMS = {
    "amazon": "https://www.amazon.in/s?k={query}",
    "flipkart": "https://www.flipkart.com/search?q={query}",
    "ikea": "https://www.ikea.com/in/en/search/?q={query}",
    "swiggy": "https://www.swiggy.com/search?query={query}",
    "zomato": "https://www.zomato.com/search?query={query}",
    "oyo": "https://www.oyorooms.com/search?location={query}",
    "myntra": "https://www.myntra.com/{query}",
    "ajio": "https://www.ajio.com/search/?text={query}",
    "meesho": "https://www.meesho.com/search?q={query}",
    "booking": "https://www.booking.com/searchresults.html?ss={query}",
}

def make_search_links(search_terms: str, platforms: list[str]) -> dict[str, str]:
    query = quote_plus(search_terms.strip())
    return {p.lower(): PLATFORMS[p.lower()].format(query=query) for p in platforms if p.lower() in PLATFORMS}
