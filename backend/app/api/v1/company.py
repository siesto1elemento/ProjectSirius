from fastapi import APIRouter, HTTPException
from app.services import scraper
from app.models.company import CompanyRatiosResponse, CompanyPriceResponse

router = APIRouter()

@router.get("/{ticker}/price", response_model=CompanyPriceResponse)
def get_company_price(ticker: str):
    """
    Retrieves key stock price data for a given company ticker using yfinance.
    For Indian stocks, append .NS (e.g., RELIANCE.NS).
    """
    price_data = scraper.get_stock_price_data(ticker.upper())
    
    if price_data.get("error"):
        raise HTTPException(status_code=404, detail=price_data.get("error"))
        
    return CompanyPriceResponse(ticker=ticker.upper(), data=price_data)


@router.get("/{ticker}/ratios", response_model=CompanyRatiosResponse)
def get_company_ratios(ticker: str):
    """
    Retrieves key financial ratios for a given company ticker by scraping.
    """
    # Note: The ticker format for scraping might be different from yfinance
    ratios = scraper.scrape_key_ratios(ticker)
    
    if ratios.get("error"):
        raise HTTPException(status_code=404, detail=ratios.get("error"))
        
    return CompanyRatiosResponse(ticker=ticker, ratios=ratios)
