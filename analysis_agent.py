from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from stock_tool import get_stock_info


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.gapgpt.app/v1")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-5.1")

if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY پیدا نشد. فایل .env را از روی .env.example بسازید."
    )

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


SYSTEM_PROMPT = """
تو یک تحلیلگر مالی بازار سرمایه ایران هستی.

قوانین:
1. قبل از تحلیل هر نماد، حتماً باید ابزار get_stock_info را اجرا کنی.
2. قیمت، حجم، درصد تغییر و ارزش بازار را فقط از خروجی Tool بگیر.
3. هیچ عدد مالی را حدس نزن یا جعل نکن.
4. اگر داده کافی برای RSI، MACD، Moving Average یا حمایت/مقاومت نداری،
   این محدودیت را شفاف اعلام کن.
5. پاسخ نهایی باید شامل وضعیت قیمت، درصد تغییر، حجم، برداشت کوتاه‌مدت،
   ریسک‌ها و محدودیت داده باشد.
6. این تحلیل توصیه خرید یا فروش نیست.
""".strip()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_info",
            "description": "دریافت اطلاعات لحظه‌ای یک نماد بورسی ایران از TSETMC",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "نماد بورسی ایران؛ مثلاً فولاد یا خودرو",
                    }
                },
                "required": ["symbol"],
                "additionalProperties": False,
            },
        },
    }
]


def _execute_tool_call(tool_call) -> dict:
    """Execute one tool call requested by the model."""
    function_name = tool_call.function.name

    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        raise RuntimeError("آرگومان Tool Call یک JSON معتبر نیست.") from exc

    if function_name != "get_stock_info":
        raise ValueError(f"Unknown tool: {function_name}")

    symbol = arguments.get("symbol")
    if not symbol:
        raise ValueError("LLM آرگومان symbol را ارسال نکرده است.")

    return get_stock_info(symbol=symbol)


def analyze_stock(
    user_request: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """Analyze an Iranian stock using mandatory Function Calling."""
    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError("user_request نمی‌تواند خالی باشد.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_request.strip()},
    ]

    first_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice={
            "type": "function",
            "function": {"name": "get_stock_info"},
        },
    )

    assistant_message = first_response.choices[0].message

    if not assistant_message.tool_calls:
        raise RuntimeError("LLM هیچ Tool Call ایجاد نکرد.")

    messages.append(assistant_message.model_dump(exclude_none=True))

    for tool_call in assistant_message.tool_calls:
        result = _execute_tool_call(tool_call)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    final_text = final_response.choices[0].message.content
    if not final_text:
        raise RuntimeError("مدل پاسخ نهایی متنی برنگرداند.")

    return final_text


if __name__ == "__main__":
    prompt = """
    نماد فولاد را تحلیل کن.
    ابتدا اطلاعات واقعی و لحظه‌ای سهم را با ابزار دریافت کن و سپس
    وضعیت کوتاه‌مدت را توضیح بده. اگر داده کافی برای RSI، MACD یا
    حمایت و مقاومت نداری، عدد ساختگی تولید نکن.
    """.strip()

    print(analyze_stock(prompt))
