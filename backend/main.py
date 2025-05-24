from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
import uvicorn

from app.models.location import (
    StoreLocation, 
    PredictionResponse, 
    LocationAnalysisResult,
    MapBounds,
    AreaRequest,
    HeatmapData
)
from app.services.data_service import DataService
from app.services.prediction_service import PredictionService

# Initialize FastAPI app
app = FastAPI(
    title="OXXO Store Location Prediction API",
    description="API for predicting optimal OXXO store locations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_service = DataService()
prediction_service = PredictionService(data_service)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "OXXO Store Location Prediction API"}

# API endpoints
@app.post("/api/predict-location", response_model=PredictionResponse)
async def predict_location(location: StoreLocation):
    try:
        return prediction_service.predict_location(location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/optimal-locations", response_model=List[StoreLocation])
async def get_optimal_locations(area: AreaRequest):
    try:
        return prediction_service.get_optimal_locations(area)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding optimal locations: {str(e)}")

@app.post("/api/analyze-location", response_model=LocationAnalysisResult)
async def analyze_location(location: StoreLocation):
    try:
        return prediction_service.analyze_location(location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/api/location-heatmap", response_model=HeatmapData)
async def get_location_heatmap(bounds: MapBounds):
    try:
        return prediction_service.generate_heatmap(bounds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation error: {str(e)}")

@app.get("/api/stores", response_model=List[StoreLocation])
async def get_stores():
    try:
        return data_service.get_all_stores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving store data: {str(e)}")

# For development - run with uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

