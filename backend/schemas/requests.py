from pydantic import BaseModel, Field
from typing import Optional

class CarFeatures(BaseModel):
    TaskName: Optional[str] = Field(..., description="Name of the task/service (e.g., Wheel alignment, Brake service)")
    Make: str = Field(..., description="Vehicle manufacturer (e.g., Toyota)")
    Model: str = Field(..., description="Vehicle model (e.g., Corolla)")
    Year: Optional[int] = Field(None, description="Year of manufacture")
    FuelType: Optional[str] = Field(None, description="Fuel type (e.g., Petrol, Diesel, Hybrid)")
    Transmission: Optional[str] = Field(None, description="Transmission type (e.g., Auto, Manual)")
    EngineSize: Optional[float] = Field(None, description="Engine displacement in litres")
    DriveType: Optional[str] = Field(None, description="Drive type (e.g., FWD, RWD, AWD)")
    Distance: Optional[float] = Field(None, description="Vehicle odometer reading (km)")
    Months: Optional[float] = Field(None, description="Months since service or warranty (if applicable)")
    AdjustedPrice: Optional[float] = Field(None, description="Historical adjusted price (optional)")

class RegistrationRequest(BaseModel):
    Registration: str = Field(..., description="Vehicle registration number")

class PredictRequest(BaseModel):
    model_name: str = Field(..., description="Which model to use: one of Capped, Logbook, Prescribed, Repair")
    features: CarFeatures = Field(..., description="Vehicle / Task feature object")

class HistoricalRequest(BaseModel):
    model_name: str = Field(..., description="Which model to use: one of Capped, Logbook, Prescribed, Repair")
    features: CarFeatures = Field(..., description="Vehicle / Task feature object")
    prediction: float = Field(..., description="Predicted price from /predict endpoint")
    months: Optional[float] = Field(None, description="Months of service (if applicable)")
    distance: Optional[float] = Field(None, description="Vehicle odometer reading (km)")
