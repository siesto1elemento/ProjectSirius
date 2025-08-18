from typing import Dict, Any, List
import yfinance as yf


def get_stock_price_data(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetches key stock price data for a given ticker symbol using yfinance.
    For Indian stocks on NSE, '.NS' should be appended (e.g., 'RELIANCE.NS').
    """
    try:
        # Append .NS for Indian tickers if not already present
        if ".NS" not in ticker_symbol.upper() and ".BO" not in ticker_symbol.upper():
             # This is a simple heuristic, might need refinement
            ticker_symbol += ".NS"

        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.info

        # Check if the market is open to get current price, otherwise fallback
        current_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice')

        if not current_price:
            return {"error": f"Could not retrieve price for {ticker_symbol}. It might be an invalid ticker or delisted."}

        price_data = {
            "shortName": stock_info.get('shortName'),
            "symbol": ticker_symbol,
            "currentPrice": current_price,
            "currency": stock_info.get('currency'),
            "previousClose": stock_info.get('previousClose'),
            "dayHigh": stock_info.get('dayHigh'),
            "dayLow": stock_info.get('dayLow'),
            "fiftyTwoWeekHigh": stock_info.get('fiftyTwoWeekHigh'),
            "fiftyTwoWeekLow": stock_info.get('fiftyTwoWeekLow'),
            "TrailingPE": stock_info.get('trailingPE')
        }
        return price_data

    except Exception as e:
        return {"error": f"An error occurred with yfinance for ticker '{ticker_symbol}': {e}"}


def get_price_earning_data(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetches P/E ratio for a given ticker symbol using yfinance.
    For Indian stocks on NSE, '.NS' should be appended (e.g., 'RELIANCE.NS').
    """
    try:
        # Append .NS for Indian tickers if not already present
        if ".NS" not in ticker_symbol.upper() and ".BO" not in ticker_symbol.upper():
             # This is a simple heuristic, might need refinement
            ticker_symbol += ".NS"

        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.info

        # Check if the market is open to get current price, otherwise fallback
        current_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice')

        if not current_price:
            return {"error": f"Could not retrieve price for {ticker_symbol}. It might be an invalid ticker or delisted."}

        price_data = {
            "shortName": stock_info.get('shortName'),
            "symbol": ticker_symbol,
            "TrailingPE": stock_info.get('trailingPE'),
            "ForwardPE": stock_info.get('forwardPE')
        }
        return price_data

    except Exception as e:
        return {"error": f"An error occurred with yfinance for ticker '{ticker_symbol}': {e}"}


def get_financial_statement(ticker_symbol: str, statement_type: str, frequency: str = "annual") -> Dict[str, Any]:
    """
    Fetches a company's financial statements (income statement, balance sheet, or cash flow).
    
    :param ticker_symbol: The stock ticker symbol (e.g., 'RELIANCE.NS').
    :param statement_type: The type of statement to fetch. Must be one of 'income', 'balance', or 'cashflow'.
    :param frequency: The frequency of the report. Must be 'annual' or 'quarterly'.
    """
    try:
        if ".NS" not in ticker_symbol.upper() and ".BO" not in ticker_symbol.upper():
            ticker_symbol += ".NS"
        
        stock = yf.Ticker(ticker_symbol)
        
        statement_df = None
        if statement_type.lower() == 'income':
            statement_df = stock.income_stmt if frequency.lower() == 'annual' else stock.quarterly_income_stmt
        elif statement_type.lower() == 'balance':
            statement_df = stock.balance_sheet if frequency.lower() == 'annual' else stock.quarterly_balance_sheet
        elif statement_type.lower() == 'cashflow':
            statement_df = stock.cashflow if frequency.lower() == 'annual' else stock.quarterly_cashflow
        else:
            return {"error": "Invalid statement_type. Must be 'income', 'balance', or 'cashflow'."}

        # yfinance returns a pandas DataFrame. We convert it to a dictionary.
        # The index contains timestamps, which we convert to strings for JSON compatibility.
        statement_dict = statement_df.to_dict()
        return {str(k): v for k, v in statement_dict.items()}

    except Exception as e:
        return {"error": f"An error occurred for ticker '{ticker_symbol}': {e}"}


def get_company_profile(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetches key profile information for a company, such as sector, industry, and business summary.
    """
    try:
        if ".NS" not in ticker_symbol.upper() and ".BO" not in ticker_symbol.upper():
            ticker_symbol += ".NS"
        
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        profile_data = {
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.g_et("industry"),
            "fullTimeEmployees": info.get("fullTimeEmployees"),
            "longBusinessSummary": info.get("longBusinessSummary"),
            "website": info.get("website"),
            "city": info.get("city"),
            "country": info.get("country")
        }
        return profile_data

    except Exception as e:
        return {"error": f"An error occurred for ticker '{ticker_symbol}': {e}"}


def get_latest_news(ticker_symbol: str) -> List[Dict[str, Any]]:
    """
    Fetches the latest news articles for a given company.
    """
    try:
        if ".NS" not in ticker_symbol.upper() and ".BO" not in ticker_symbol.upper():
            ticker_symbol += ".NS"
        
        stock = yf.Ticker(ticker_symbol)
        # The 'news' attribute returns a list of dictionaries
        news = stock.news
        return news if news else [{"message": "No recent news found."}]

    except Exception as e:
        return [{"error": f"An error occurred for ticker '{ticker_symbol}': {e}"}]

