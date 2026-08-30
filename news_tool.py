from __future__ import annotations

import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def search_stock_news(symbol: str, max_results: int = 5) -> dict:
    """
    اخبار مرتبط با یک نماد بورسی ایران را در اینترنت جستجو می‌کند.

    Args:
        symbol (str): نماد بورسی، مثلاً "فولاد".
        max_results (int): حداکثر تعداد نتایج بین 1 تا 10.

    Returns:
        dict: نماد، عبارت جستجو و فهرست نتایج خبری.

    Raises:
        ValueError: اگر ورودی نامعتبر باشد.
        RuntimeError: اگر کلید Tavily موجود نباشد یا جستجو شکست بخورد.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("نماد سهم نمی‌تواند خالی باشد.")
    if not 1 <= max_results <= 10:
        raise ValueError("max_results باید بین 1 و 10 باشد.")

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY در فایل .env تعریف نشده است.")

    query = f"آخرین اخبار بورس نماد {symbol.strip()} شرکت {symbol.strip()} کدال"
    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query,
            topic="news",
            max_results=max_results,
            search_depth="advanced",
        )
    except Exception as exc:
        raise RuntimeError(
            f"جستجوی اخبار نماد '{symbol.strip()}' ناموفق بود."
        ) from exc

    results = [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content"),
            "score": item.get("score"),
        }
        for item in response.get("results", [])
    ]

    return {
        "symbol": symbol.strip(),
        "query": query,
        "results": results,
    }
