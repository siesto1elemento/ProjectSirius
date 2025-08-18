from pydantic import BaseModel
from typing import Dict, Optional, Any

class KeyRatios(BaseModel):
    """
    Represents the key financial ratios for a company.
    """
    pe_ratio: Optional[str] = None
    roe: Optional[str] = None
    debt_to_equity: Optional[str] = None
    # Add other ratios as needed

class CompanyRatiosResponse(BaseModel):
    """
    The response model for the company ratios endpoint.
    """
    ticker: str
    ratios: Dict[str, str]

class CompanyPriceResponse(BaseModel):
    """
    The response model for the company price data endpoint.
    """
    ticker: str
    data: Dict[str, Any]
