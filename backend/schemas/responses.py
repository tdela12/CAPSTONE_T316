from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RegistrationResponse(BaseModel):
    Registration: str = Field(..., description="Vehicle registration number")
    Make: Optional[str] = Field(None, description="Vehicle manufacturer (e.g., Toyota)")
    Model: Optional[str] = Field(None, description="Vehicle model (e.g., Corolla)")
    Year: Optional[int] = Field(None, description="Year of manufacture")
    FuelType: Optional[str] = Field(None, description="Fuel type (e.g., Petrol, Diesel, Hybrid)")
    EngineSize: Optional[float] = Field(None, description="Engine displacement in litres")
    Transmission: Optional[str] = Field(None, description="Transmission type (e.g., Auto, Manual)")
    DriveType: Optional[str] = Field(None, description="Drive type (e.g., FWD, RWD, AWD)")

class PrefilteredResponse(BaseModel):
    Make: list[str] = Field(..., description="Unique Vehicle manufacturer Categories (e.g., Toyota)")
    Model: list[str] = Field(..., description="Unique Vehicle model Categories(e.g., Corolla)")
    Year: Optional[list[int]] = Field(None, description="Unique Years of manufacture")
    EngineSize: Optional[list[float]] = Field(None, description="Unique Engine displacement in litres Categories")
    Distance: Optional[list[float]] = Field(None, description="Unique Vehicle odometer reading Categories (km)")
    Months: Optional[list[float]] = Field(None, description="Months since service or warranty (if applicable)")
    
class PredictPlotOutputs(BaseModel):
    shap_png: Optional[str] = Field(None, description="Base64 PNG of SHAP waterfall plot")

class HistoricalPlotOutputs(BaseModel):
    boxplot_png: Optional[str] = Field(None, description="Base64 PNG of boxplot (if applicable)")
    histogram_png: Optional[str] = Field(None, description="Base64 PNG of histogram (if applicable)")
    month_vs_price_png: Optional[str] = Field(None, description="Base64 PNG of Months vs Price scatter")
    distance_vs_price_png: Optional[str] = Field(None, description="Base64 PNG of Distance vs Price scatter")

class ComparisonResult(BaseModel):
    predicted_price: float
    mean: Optional[float]
    median: Optional[float]
    iqr_low: Optional[float]
    iqr_high: Optional[float]
    within_iqr: bool
    z_from_median: float
    confidence: str
    percentile: float

class SummaryResult(BaseModel):
    min: Optional[float]
    max: Optional[float]
    median: Optional[float]
    iqr_low: Optional[float]
    iqr_high: Optional[float]
    count: Optional[float]

class PredictResponse(BaseModel):
    model: str
    prediction: float
    features: dict
    plots: PredictPlotOutputs
    message: Optional[str] = None

class HistoricalResponse(BaseModel):
    summary: Optional[SummaryResult] = None
    comparison: Optional[ComparisonResult] = None
    plots: HistoricalPlotOutputs
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[Dict]] = None  # now accepts a list of dicts