import json
import httpx
import jmespath
from urllib.parse import quote
from typing import Optional
import asyncio

INSTAGRAM_ACCOUNT_DOCUMENT_ID = "9310670392322965"

client = httpx.Client(
    headers={
        # this is internal ID of an instegram backend app. It doesn't change often.
        "x-ig-app-id": "936619743392459",
        # use browser-like features
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

async def scrape_user_posts(username: str, page_size=12, max_pages: Optional[int] = None):
    """Scrape all posts of an Instagram user given the username."""
    base_url = "https://www.instagram.com/graphql/query"
    variables = {
        "after": None,
        "before": None,
        "data": {
            "count": page_size,
            "include_reel_media_seen_timestamp": True,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "first": page_size,
        "last": None,
        "username": f"{username}",
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
        "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
    }

    prev_cursor = None
    _page_number = 1

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as session:
        while True:
            body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={INSTAGRAM_ACCOUNT_DOCUMENT_ID}"

            response = await session.post(
                base_url,
                data=body,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()

            with open("ts2.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            posts = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
            for post in posts["edges"]:
                yield post["node"]

            page_info = posts["page_info"]
            if not page_info["has_next_page"]:
                print(f"scraping posts page {_page_number}")
                break

            if page_info["end_cursor"] == prev_cursor:
                print("found no new posts, breaking")
                break

            prev_cursor = page_info["end_cursor"]
            variables["after"] = page_info["end_cursor"]
            _page_number += 1

            if max_pages and _page_number > max_pages:
                break



def scrape_user(username: str):
    """Scrape Instagram user's data"""
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

def parse_user(data: dict) -> dict:
    """Parse instagram user's hidden web dataset for user's data"""
    result = jmespath.search(
        """{
        name: full_name,
        username: username,
        id: id,
        category: category_name,
        business_category: business_category_name,
        phone: business_phone_number,
        email: business_email,
        posts: edge_owner_to_timeline_media.edges[].node.{
            id: id,
            title: title,
            captions: edge_media_to_caption.edges[].node.text,
            thumbnail_resources: thumbnail_resources[].src
            }
    }""",
        data,
    )
    return result