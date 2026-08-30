import json

from stock_tool import get_stock_info


print("Valid symbol:")
result = get_stock_info("فولاد")
print(json.dumps(result, ensure_ascii=False, indent=2))

print("\nInvalid symbol:")
try:
    get_stock_info("XYZ123")
except ValueError as exc:
    print(f"Expected ValueError: {exc}")
