from datetime import datetime

import pytest

import stock_tool


class FakeRealtimeData:
    last_price = 52_500
    yesterday_price = 50_000
    volume = 12_000_000
    market_cap = 500_000_000_000
    last_date = datetime(2026, 8, 30, 12, 30, 0)


class FakeTicker:
    def __init__(self, symbol: str):
        if symbol == "XYZ123":
            raise ValueError("Symbol not found")
        self.title = "شرکت تست"

    def get_ticker_real_time_info_response(self):
        return FakeRealtimeData()


def test_valid_symbol(monkeypatch):
    monkeypatch.setattr(stock_tool.tse, "Ticker", FakeTicker)

    result = stock_tool.get_stock_info("فولاد")

    assert result["symbol"] == "فولاد"
    assert result["name"] == "شرکت تست"
    assert result["last_price"] == 5_250.0
    assert result["price_change_percent"] == 5.0
    assert result["volume"] == 12_000_000
    assert result["market_cap"] == 50_000_000_000.0


def test_normalizes_arabic_characters(monkeypatch):
    monkeypatch.setattr(stock_tool.tse, "Ticker", FakeTicker)

    result = stock_tool.get_stock_info("فولاد ")
    assert result["symbol"] == "فولاد"


def test_invalid_symbol(monkeypatch):
    monkeypatch.setattr(stock_tool.tse, "Ticker", FakeTicker)

    with pytest.raises(ValueError, match="TSETMC یافت نشد"):
        stock_tool.get_stock_info("XYZ123")


def test_empty_symbol():
    with pytest.raises(ValueError):
        stock_tool.get_stock_info("")
