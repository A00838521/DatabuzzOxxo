from pydantic import BaseModel, Field, validator, model_validator
from typing import List, Optional, Dict, Any
import re

class StoreLocation(BaseModel):
    """Store location model with relevant attributes for prediction"""
    tiendaId: Optional[int] = Field(None, description="Store ID, optional for new locations")
    plazaCve: int = Field(..., description="Plaza code", ge=1)
    nivelSocioeconomico: str = Field(..., description="Socioeconomic level", min_length=1)
    entorno: str = Field(..., description="Environment type", min_length=1)
    mts2Ventas: float = Field(..., description="Sales area in square meters", gt=0)
    puertasRefrig: int = Field(..., description="Number of refrigerator doors", ge=0)
    cajonesEstacionamiento: int = Field(..., description="Number of parking spaces", ge=0)
    latitud: float = Field(..., description="Latitude coordinate", ge=0, le=90)
    longitud: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    segmentoMaestro: str = Field(..., description="Master segment", min_length=1)
    
    @validator('nivelSocioeconomico')
    def validate_nivel_socioeconomico(cls, v):
        allowed_values = ['A', 'AB', 'B', 'BC', 'C', 'CD', 'D']
        if v not in allowed_values:
            raise ValueError(f"nivelSocioeconomico must be one of {allowed_values}")
        return v
    
    @validator('entorno')
    def validate_entorno(cls, v):
        allowed_values = ['Base', 'Hogar', 'Peatonal', 'Receso']
        if v not in allowed_values:
            raise ValueError(f"entorno must be one of {allowed_values}")
        return v
    
    @validator('segmentoMaestro')
    def validate_segmento_maestro(cls, v):
        allowed_values = ['Barrio Competido', 'Clásico', 'Hogar Reunión', 'Oficinistas', 'Parada Técnica']
        if v not in allowed_values:
            raise ValueError(f"segmentoMaestro must be one of {allowed_values}")
        return v
    
    @validator('latitud')
    def validate_latitud(cls, v):
        # Mexican territory latitude range (approximately)
        if not (14.0 <= v <= 33.0):
            raise ValueError("Latitude should be within Mexican territory (approximately 14°N to 33°N)")
        return v
    
    @validator('longitud')
    def validate_longitud(cls, v):
        # Mexican territory longitude range (approximately)
        if not (-118.5 <= v <= -86.5):
            raise ValueError("Longitude should be within Mexican territory (approximately -118.5°W to -86.5°W)")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "plazaCve": 1,
                "nivelSocioeconomico": "C",
                "entorno": "Hogar",
                "mts2Ventas": 100.0,
                "puertasRefrig": 12,
                "cajonesEstacionamiento": 0,
                "latitud": 25.67,
                "longitud": -100.22,
                "segmentoMaestro": "Clásico"
            }
        }
    }

class PredictionResponse(BaseModel):
    """Response model for store location prediction"""
    score: float = Field(..., description="Prediction score (0-1)", ge=0, le=1)
    expectedSales: float = Field(..., description="Expected monthly sales in MXN", ge=0)
    probability: float = Field(..., description="Probability of success (0-1)", ge=0, le=1)
    recommendation: str = Field(..., description="Recommendation text")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "score": 0.85,
                "expectedSales": 480000.0,
                "probability": 0.78,
                "recommendation": "Esta ubicación tiene un alto potencial para una tienda OXXO, con ventas esperadas por encima del promedio."
            }
        }
    }

class SalesForecast(BaseModel):
    """Monthly sales forecast model"""
    month: str = Field(..., description="Month identifier (YYYYMM)")
    amount: float = Field(..., description="Forecasted sales amount", ge=0)
    
    @validator('month')
    def validate_month(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('Month must be in YYYYMM format')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "month": "202405",
                "amount": 485000.0
            }
        }
    }

class MapPoint(BaseModel):
    """Point on a map with associated score"""
    id: str = Field(..., description="Unique identifier for the point")
    lat: float = Field(..., description="Latitude coordinate", ge=0, le=90)
    lng: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    score: float = Field(..., description="Location score (0-1)", ge=0, le=1)
    color: str = Field(..., description="Color code for the point")
    
    @validator('color')
    def validate_color(cls, v):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "loc1",
                "lat": 25.67,
                "lng": -100.22,
                "score": 0.85,
                "color": "#10b981"
            }
        }
    }

class LocationAnalysisResult(BaseModel):
    """Detailed analysis result for a store location"""
    location: StoreLocation = Field(..., description="The analyzed store location")
    prediction: PredictionResponse = Field(..., description="Prediction results")
    nearbyStores: Optional[List[StoreLocation]] = Field(None, description="Nearby existing stores")
    salesForecast: Optional[List[SalesForecast]] = Field(None, description="Monthly sales forecast")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "location": {
                    "plazaCve": 1,
                    "nivelSocioeconomico": "C",
                    "entorno": "Hogar",
                    "mts2Ventas": 100.0,
                    "puertasRefrig": 12,
                    "cajonesEstacionamiento": 0,
                    "latitud": 25.67,
                    "longitud": -100.22,
                    "segmentoMaestro": "Clásico"
                },
                "prediction": {
                    "score": 0.85,
                    "expectedSales": 480000.0,
                    "probability": 0.78,
                    "recommendation": "Esta ubicación tiene un alto potencial para una tienda OXXO."
                },
                "nearbyStores": [],
                "salesForecast": [
                    {"month": "202405", "amount": 485000.0},
                    {"month": "202406", "amount": 495000.0}
                ]
            }
        }
    }

class MapBounds(BaseModel):
    """Geographic boundaries for heatmap generation"""
    north: float = Field(..., description="North latitude boundary", ge=0, le=90)
    south: float = Field(..., description="South latitude boundary", ge=0, le=90)
    east: float = Field(..., description="East longitude boundary", ge=-180, le=180)
    west: float = Field(..., description="West longitude boundary", ge=-180, le=180)
    
    @model_validator(mode='after')
    def validate_bounds(self) -> 'MapBounds':
        north, south = self.north, self.south
        east, west = self.east, self.west
        
        if north is not None and south is not None and north <= south:
            raise ValueError("North must be greater than south")
        
        if east is not None and west is not None and east <= west:
            raise ValueError("East must be greater than west")
            
        return self
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "north": 25.75,
                "south": 25.65,
                "east": -100.15,
                "west": -100.30
            }
        }
    }

class AreaRequest(BaseModel):
    """Area request for finding optimal locations"""
    lat: float = Field(..., description="Center latitude", ge=0, le=90)
    lng: float = Field(..., description="Center longitude", ge=-180, le=180)
    radius: float = Field(..., description="Search radius in kilometers", gt=0, le=50)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "lat": 25.67,
                "lng": -100.22,
                "radius": 5.0
            }
        }
    }

class HeatmapData(BaseModel):
    """Heatmap data with points and center coordinates"""
    points: List[MapPoint] = Field(..., description="Array of points with scores")
    centerLat: float = Field(..., description="Center latitude for the map", ge=0, le=90)
    centerLng: float = Field(..., description="Center longitude for the map", ge=-180, le=180)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "points": [
                    {
                        "id": "loc1",
                        "lat": 25.67,
                        "lng": -100.22,
                        "score": 0.85,
                        "color": "#10b981"
                    },
                    {
                        "id": "loc2",
                        "lat": 25.68,
                        "lng": -100.23,
                        "score": 0.65,
                        "color": "#3b82f6"
                    }
                ],
                "centerLat": 25.675,
                "centerLng": -100.225
            }
        }
    }

