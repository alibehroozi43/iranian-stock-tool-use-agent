from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytse_client as tse


TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def _normalize_symbol(symbol: str) -> str:
    """Normalize common Arabic characters used in Persian stock symbols."""
    return symbol.strip().replace("ي", "ی").replace("ك", "ک")


def get_stock_info(symbol: str) -> dict:
    """
    اطلاعات لحظه‌ای یک نماد بورسی ایران را از TSETMC بازمی‌گرداند.

    Args:
        symbol (str): نماد سهم به فارسی یا انگلیسی، دقیقاً همانطور که در
            TSETMC ثبت شده است. مثال: "فولاد"

    Returns:
        dict: دیکشنری با کلیدهای زیر:
            - symbol (str): نماد سهم
            - name (str): نام کامل شرکت
            - last_price (float): آخرین قیمت معامله‌شده (تومان)
            - price_change_percent (float): درصد تغییر نسبت به روز قبل
            - volume (int): حجم معاملات
            - market_cap (float | None): ارزش بازار در صورت موجود بودن
            - last_update (str): زمان آخرین به‌روزرسانی به فرمت ISO 8601

    Raises:
        ValueError: اگر نماد وارد‌شده در TSETMC یافت نشود.
    """
    if not isinstance(symbol, str):
        raise ValueError("نماد سهم باید از نوع رشته (str) باشد.")

    symbol = _normalize_symbol(symbol)
    if not symbol:
        raise ValueError("نماد سهم نمی‌تواند خالی باشد.")

    try:
        ticker = tse.Ticker(symbol)
    except Exception as exc:
        raise ValueError(f"نماد '{symbol}' در TSETMC یافت نشد.") from exc

    try:
        realtime = ticker.get_ticker_real_time_info_response()
    except Exception as exc:
        raise ValueError(
            f"اطلاعات لحظه‌ای نماد '{symbol}' از TSETMC قابل دریافت نیست."
        ) from exc

    last_price_rial = realtime.last_price
    yesterday_price_rial = realtime.yesterday_price
    market_cap_rial = getattr(realtime, "market_cap", None)
    volume = realtime.volume
    last_date = realtime.last_date

    if last_price_rial is None:
        raise ValueError(
            f"آخرین قیمت معامله برای نماد '{symbol}' در حال حاضر موجود نیست."
        )

    last_price_toman = float(last_price_rial) / 10.0
    market_cap_toman = (
        float(market_cap_rial) / 10.0
        if market_cap_rial is not None
        else None
    )

    if yesterday_price_rial not in (None, 0):
        price_change_percent = (
            (float(last_price_rial) - float(yesterday_price_rial))
            / float(yesterday_price_rial)
        ) * 100.0
    else:
        price_change_percent = 0.0

    if isinstance(last_date, datetime):
        if last_date.tzinfo is None:
            last_date = last_date.replace(tzinfo=TEHRAN_TZ)
        last_update = last_date.isoformat()
    else:
        last_update = datetime.now(TEHRAN_TZ).isoformat()

    try:
        company_name = ticker.title
    except Exception:
        company_name = symbol

    return {
        "symbol": symbol,
        "name": company_name,
        "last_price": round(last_price_toman, 2),
        "price_change_percent": round(price_change_percent, 2),
        "volume": int(volume or 0),
        "market_cap": (
            round(market_cap_toman, 2)
            if market_cap_toman is not None
            else None
        ),
        "last_update": last_update,
    }


if __name__ == "__main__":
    print(get_stock_info("فولاد"))
