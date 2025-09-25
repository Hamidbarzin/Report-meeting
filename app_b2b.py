# app_b2b.py
import streamlit as st
import pandas as pd
import requests, os, re, time
from typing import List, Dict, Optional

st.set_page_config(
    page_title="Toronto B2B Lead Generator",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "YOUR_API_KEY_HERE"

# ---------- Helpers ----------
def geocode_location(location: str) -> Optional[Dict[str, float]]:
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        r = requests.get(url, params={"address": location, "key": GOOGLE_API_KEY}, timeout=12)
        data = r.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}
    except Exception:
        pass
    return None

def build_queries(search_term: str, focuses: List[str], location: str) -> List[str]:
    # کلمات کلیدی پیش‌فرض برای B2B
    focus_map = {
        "Importers": ["importer", "import"],
        "Distributors / Wholesalers": ["distributor", "wholesale", "wholesaler"],
        "Suppliers / Manufacturers": ["supplier", "manufacturer", "factory"],
        "Fulfillment / 3PL": ["fulfillment center", "3pl", "order fulfillment"],
        "Logistics & Freight": ["logistics", "freight", "shipping company", "forwarder"],
        "E-commerce / Online Retail": ["ecommerce", "online store", "online retailer"]
    }
    tokens = []
    for f in focuses:
        tokens += focus_map.get(f, [])
    if not tokens:
        tokens = ["importer", "distributor", "wholesale", "supplier", "fulfillment", "3pl", "logistics", "ecommerce"]

    # یک یا چند کوئری می‌سازیم تا کوریج بالا برود
    queries = []
    base = (search_term or "").strip()
    for t in tokens:
        if base:
            queries.append(f"{t} {base} in {location}")
        else:
            queries.append(f"{t} in {location}")
    # dedupe
    return list(dict.fromkeys(queries))

def classify_flags(name: str, types: List[str], category_hint: str = "") -> Dict[str, bool]:
    n = (name or "").lower()
    t = " ".join(types or []).lower()
    h = (category_hint or "").lower()

    likely_delivery = any(k in (t + " " + n + " " + h)
                          for k in ["store", "ecommerce", "online", "retail", "shop", "supermarket"])

    potential_worldwide = any(k in (t + " " + n + " " + h)
                              for k in ["import", "export", "wholesale", "global", "international", "distributor"])

    is_logistics = any(k in (t + " " + n + " " + h)
                       for k in ["logistics", "freight", "courier", "3pl", "forwarder", "shipping"])

    return {
        "likely_delivery": bool(likely_delivery),
        "potential_worldwide_shipping": bool(potential_worldwide),
        "is_logistics": bool(is_logistics)
    }

def fetch_places_textsearch(query: str, loc_bias: Optional[Dict[str, float]] = None, max_results: int = 20):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_API_KEY}
    if loc_bias:
        params.update({"location": f'{loc_bias["lat"]},{loc_bias["lng"]}', "radius": 30000})  # ~30km
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])[:max_results]

def fetch_place_details(place_id: str) -> Dict[str, Optional[str]]:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    fields = "formatted_phone_number,international_phone_number,website,types"
    r = requests.get(url, params={"place_id": place_id, "fields": fields, "key": GOOGLE_API_KEY}, timeout=15)
    data = r.json().get("result", {}) if r.ok else {}
    return {
        "phone": data.get("formatted_phone_number") or data.get("international_phone_number"),
        "website": data.get("website"),
        "types": data.get("types", [])
    }

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
def try_find_email(website: Optional[str]) -> Optional[str]:
    if not website:
        return None
    candidates = [website.rstrip("/")]
    for tail in ["/contact", "/contact-us", "/about", "/support"]:
        candidates.append(website.rstrip("/") + tail)
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in candidates:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if not resp.ok: 
                continue
            m = re.search(EMAIL_REGEX, resp.text, re.IGNORECASE)
            if m:
                return m.group(0)
        except Exception:
            continue
    return None

def maps_url(place_id: str) -> str:
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"

def to_rows(raw: Dict[str, Dict]) -> List[Dict]:
    return list(raw.values())

# ---------- UI & Main ----------
def main():
    st.title("🏭 Toronto B2B Lead Generator")
    st.markdown("Find **importers, distributors, wholesalers, suppliers, fulfillment/3PL, logistics, and e-commerce** companies in Toronto.")

    with st.sidebar:
        st.header("🔍 Search Filters")
        search_term = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., electronics, auto parts, beauty, medical devices"
        )

        business_focus = st.multiselect(
            "Business Focus",
            options=[
                "Importers",
                "Distributors / Wholesalers",
                "Suppliers / Manufacturers",
                "Fulfillment / 3PL",
                "Logistics & Freight",
                "E-commerce / Online Retail",
            ],
            default=["Distributors / Wholesalers", "Suppliers / Manufacturers", "Logistics & Freight"]
        )

        location = st.text_input("Location", value="Toronto, ON")
        max_results = st.slider("Max per query", 10, 100, 20, step=10)
        use_google_details = st.checkbox("Enrich with phone + website (Places Details)", value=True)
        try_email = st.checkbox("Try to extract email from website (beta)", value=False,
                                help="Best-effort: parses website/contact pages if accessible.")
        data_source = st.selectbox("Data Source", options=["Google Places API", "Demo Data"], index=0)
        search_button = st.button("🔎 Search Businesses", type="primary")

    if search_button:
        if data_source == "Demo Data":
            st.warning("Demo Data is disabled for B2B mode. Switch to Google Places API.")
            return

        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
            st.error("GOOGLE_API_KEY is missing. Set it in environment or replace placeholder in code.")
            return

        with st.spinner("Searching Google Places…"):
            try:
                bias = geocode_location(location)
                queries = build_queries(search_term, business_focus, location)

                raw: Dict[str, Dict] = {}  # place_id -> row
                for q in queries:
                    results = fetch_places_textsearch(q, bias, max_results=max_results)
                    for b in results:
                        pid = b.get("place_id")
                        if not pid or pid in raw:
                            continue
                        base_types = b.get("types", [])
                        addr = b.get("formatted_address")
                        name = b.get("name")
                        category = ", ".join(base_types) if base_types else ""

                        row = {
                            "name": name,
                            "category": category,
                            "phone": None,
                            "email": None,
                            "address": addr,
                            "url": maps_url(pid),
                            "rating": b.get("rating"),
                            "review_count": b.get("user_ratings_total", 0),
                            "place_id": pid,
                        }
                        # initial flags from textsearch
                        flags = classify_flags(name, base_types, category)
                        row.update(flags)
                        raw[pid] = row

                # Enrich with phone + website + (optional) email
                if use_google_details and raw:
                    for pid, row in list(raw.items()):
                        details = fetch_place_details(pid)
                        t = details.get("types") or []
                        row["phone"] = details.get("phone") or row.get("phone")
                        row["website"] = details.get("website")
                        # Re-evaluate flags with more types
                        row.update(classify_flags(row["name"], t, row.get("category", "")))
                        if try_email and not row.get("email"):
                            row["email"] = try_find_email(row.get("website"))

                businesses = to_rows(raw)

                if not businesses:
                    st.info("No companies found. Try different keywords (e.g., 'auto parts', 'beauty', 'medical').")
                    return

                display_results(businesses)

            except requests.HTTPError as http_err:
                st.error(f"HTTP error: {http_err}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

def display_results(businesses: List[Dict]) -> None:
    st.header(f"📊 Found {len(businesses)} Businesses")
    df = pd.DataFrame(businesses)

    column_order = [
        "name", "category", "phone", "email", "website", "address",
        "url", "rating", "review_count",
        "likely_delivery", "potential_worldwide_shipping", "is_logistics"
    ]
    available = [c for c in column_order if c in df.columns]
    df_display = df[available]

    st.dataframe(df_display, use_container_width=True, height=460)

    col1, col2, col3 = st.columns(3)
    with col1:
        csv_data = df_display.to_csv(index=False)
        st.download_button("📥 Export to CSV", data=csv_data,
                           file_name="toronto_b2b_leads.csv", mime="text/csv")
    with col2:
        st.metric("Total Businesses", len(businesses))
    with col3:
        st.metric("Has Website", int(df_display["website"].notna().sum()) if "website" in df_display.columns else 0)

    st.caption("Emails are best-effort (beta). For higher accuracy consider Hunter/ZeroBounce/Clearbit enrichment.")

if __name__ == "__main__":
    main()
