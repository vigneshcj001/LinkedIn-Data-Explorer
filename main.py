# backend/main.py
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from collections import Counter
import statistics

load_dotenv()

app = FastAPI(title="LinkedIn Scraper API Wrapper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"


def fetch_from_rapidapi(endpoint: str, params: dict):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    try:
        res = requests.get(f"https://{RAPIDAPI_HOST}/{endpoint}", headers=headers, params=params, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/comments")
def get_comments(post_url: str, page_number: int = 1, sort_order: str = "Most relevant"):
    return fetch_from_rapidapi("post/comments", {
        "post_url": post_url,
        "page_number": str(page_number),
        "sort_order": sort_order
    })


@app.get("/api/profile")
def get_profile(username: str):
    return fetch_from_rapidapi("profile/detail", {"username": username})


@app.get("/api/posts")
def get_posts(username: str, page_number: int = 1):
    return fetch_from_rapidapi("profile/posts", {
        "username": username,
        "page_number": str(page_number)
    })


@app.get("/api/analytics/comments")
def comment_analytics(post_url: str):
    data = fetch_from_rapidapi("post/comments", {"post_url": post_url})
    comments = data.get("data", {}).get("comments", [])
    if not comments:
        return {"success": False, "error": "No comments found"}

    authors = [c.get("author", {}).get("name") for c in comments]
    reactions = [c.get("stats", {}).get("total_reactions", 0) for c in comments]

    most_common_authors = Counter(authors).most_common(5)
    avg_reactions = statistics.mean(reactions) if reactions else 0

    return {
        "success": True,
        "summary": {
            "total_comments": len(comments),
            "unique_commenters": len(set(authors)),
            "average_reactions": avg_reactions,
            "top_commenters": most_common_authors,
            "reaction_histogram": Counter(reactions)
        },
        "comments": comments
    }


@app.get("/api/company")
def get_company(identifier: str):
    """Fetch company details by LinkedIn identifier."""
    return fetch_from_rapidapi("companies/detail", {"identifier": identifier})


