from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.location import (
    StoreLocation, 
    PredictionResponse, 
    LocationAnalysisResult,
    MapBounds,
    AreaRequest,
    HeatmapData
)
from app.services.prediction_service import PredictionService
from app.services.data_service import DataService

router = APIRouter()

# Create service instances
data_service = DataService()
prediction_service = PredictionService(data_service)

@router.post("/predict-location", response_model=PredictionResponse)
async def predict_location(location: StoreLocation):
    """
    Predict the performance of a store at the given location.
    
    Args:
        location: Store location data
        
    Returns:
        PredictionResponse with prediction results
    """
    try:
        prediction = prediction_service.predict_location(location)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-location", response_model=LocationAnalysisResult)
async def analyze_location(location: StoreLocation):
    """
    Perform detailed analysis of a store location.
    
    Args:
        location: Store location data
        
    Returns:
        LocationAnalysisResult with detailed analysis
    """
    try:
        analysis = prediction_service.analyze_location(location)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimal-locations", response_model=List[StoreLocation])
async def get_optimal_locations(area: AreaRequest):
    """
    Find optimal store locations within a specified area.
    
    Args:
        area: Area request with center coordinates and radius
        
    Returns:
        List of optimal store locations
    """
    try:
        locations = prediction_service.get_optimal_locations(area)
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-heatmap", response_model=HeatmapData)
async def generate_heatmap(bounds: MapBounds):
    """
    Generate a heatmap of store location quality within geographic bounds.
    
    Args:
        bounds: Geographic boundaries
        
    Returns:
        HeatmapData with points and center coordinates
    """
    try:
        heatmap = prediction_service.generate_heatmap(bounds)
        return heatmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

