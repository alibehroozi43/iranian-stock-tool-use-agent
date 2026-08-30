# Iranian Stock Tool-Use Agent

A compact educational project for **LLM Tool Use / Function Calling** with Tehran Stock Exchange (TSETMC) data.

The project retrieves a real-time snapshot for an Iranian stock symbol, returns a structured JSON-compatible dictionary, and lets an OpenAI-compatible LLM call the tool before producing a short financial analysis.

## Features

- `get_stock_info(symbol)` with type hints and Google-style docstring
- Input validation with clear `ValueError` messages
- Separate JSON Schema for Function Calling
- Rial-to-Toman conversion for price and market cap
- Forced tool use before the LLM analysis
- GapGPT/OpenAI-compatible endpoint configuration through `.env`
- Smoke test and unit tests
- Optional Tavily news-search tool
- No API keys committed to Git

## Project structure

```text
Agent_Stock/
├── analysis_agent.py
├── stock_tool.py
├── schema.json
├── smoke_test.py
├── function_call_payload_demo.py
├── news_tool.py
├── news_schema.json
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
└── tests/
    └── test_stock_tool.py
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Then put your real keys in `.env`.

## Test the stock tool

```powershell
python smoke_test.py
```

Expected behavior:

- `get_stock_info("فولاد")` returns a `dict`.
- `get_stock_info("XYZ123")` raises a clear `ValueError`.

Run unit tests:

```powershell
pytest -v
```

## Function Calling demo

```powershell
python function_call_payload_demo.py
```

The tool output is serialized directly into an LLM tool-result message:

```python
result = get_stock_info("فولاد")
tool_message = {
    "role": "tool",
    "tool_call_id": "call_123",
    "content": json.dumps(result, ensure_ascii=False),
}
```

## Run the financial agent

Set these values in `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.gapgpt.app/v1
LLM_MODEL=gpt-5.1
```

Then run:

```powershell
python analysis_agent.py
```

The first LLM request is forced to call `get_stock_info`. The returned market snapshot is then sent back to the model for the final analysis.

## Technical-analysis limitation

The required tool only returns a current market snapshot. It does **not** provide enough historical OHLC data to calculate indicators such as RSI, MACD, moving averages, or reliable support/resistance levels.

The system prompt therefore instructs the model to state this limitation rather than fabricate indicator values.

## Optional news tool

`news_tool.py` uses Tavily to search for recent news related to a symbol. Add `TAVILY_API_KEY` to `.env` before using it.

## Security

Never commit `.env`. This repository includes only `.env.example`.

If an API key has ever been exposed publicly, revoke it and create a new one.

## Disclaimer

This project is for educational purposes only and is not financial or investment advice.
