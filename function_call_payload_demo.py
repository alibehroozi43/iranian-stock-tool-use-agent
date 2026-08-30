import json

from stock_tool import get_stock_info


result = get_stock_info("فولاد")
tool_message = {
    "role": "tool",
    "tool_call_id": "call_123",
    "content": json.dumps(result, ensure_ascii=False),
}

print(json.dumps(tool_message, ensure_ascii=False, indent=2))
