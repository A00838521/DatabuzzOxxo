import os
import numpy as np
import pandas as pd
import pickle
import logging
import uuid
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.spatial.distance import cdist
import joblib
import shap
from pathlib import Path

from app.models.location import (
    StoreLocation, 
    PredictionResponse, 
    LocationAnalysisResult,
    MapBounds,
    AreaRequest,
    HeatmapData,
    MapPoint,
    SalesForecast
)
from app.services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service for making predictions about store locations.
    Uses trained machine learning models to predict store performance.
    """
    
    def __init__(self, data_service: DataService, model_dir: Optional[str] = None):
        """
        Initialize the prediction service.
        
        Args:
            data_service: DataService instance for data access
            model_dir: Optional directory for storing trained models
        """
        self.data_service = data_service
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'models'
        )
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Path to trained model file
        self.model_path = os.path.join(self.model_dir, 'store_location_model.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'feature_scaler.pkl')
        
        # Initialize model and scaler
        self.model = None
        self.scaler = None
        
        # Try to load existing model or train a new one
        self._load_or_train_model()
        
        logger.info("PredictionService initialized")
    
    def _load_or_train_model(self) -> None:
        """
        Load existing model from disk or train a new one if none exists.
        """
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                logger.info("Loading existing model and scaler...")
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Model and scaler loaded successfully")
            else:
                logger.info("No existing model found. Training new model...")
                self._train_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Training new model...")
            self._train_model()
    
    def _train_model(self) -> None:
        """
        Train a new prediction model using the available data.
        """
        try:
            logger.info("Getting training data...")
            X, y = self.data_service.get_training_data()
            
            # Split data into training and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train random forest model
            logger.info("Training Random Forest model...")
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            )
            
            # Fit the model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate the model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"Model trained. Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")
            logger.info(f"MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
            
            # Save the model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info(f"Model and scaler saved to {self.model_dir}")
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise ValueError(f"Failed to train model: {str(e)}")
    
    def predict_location(self, location: StoreLocation) -> PredictionResponse:
        """
        Predict the performance of a store at the given location.
        
        Args:
            location: Store location to evaluate
            
        Returns:
            PredictionResponse with prediction results
        """
        try:
            # Ensure model is loaded
            if self.model is None or self.scaler is None:
                self._load_or_train_model()
            
            # Convert location to features
            X = self.data_service.store_location_to_features(location)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            performance_ratio = self.model.predict(X_scaled)[0]
            
            # Get sales target for this environment
            sales_target = self.data_service.get_sales_target_for_environment(location.entorno)
            
            # Calculate expected sales
            expected_sales = sales_target * performance_ratio if sales_target else 0
            
            # Calculate probability of success (simplified)
            probability = self._calculate_success_probability(performance_ratio)
            
            # Calculate score (normalized between 0 and 1)
            score = min(max(performance_ratio / 1.5, 0.0), 1.0)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                score, 
                expected_sales, 
                probability, 
                location
            )
            
            # Create response
            response = PredictionResponse(
                score=score,
                expectedSales=expected_sales,
                probability=probability,
                recommendation=recommendation
            )
            
            # Log prediction
            self.data_service.save_prediction_log(
                location, 
                {
                    "score": score,
                    "expectedSales": expected_sales,
                    "probability": probability,
                    "recommendation": recommendation,
                    "performance_ratio": float(performance_ratio)
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise ValueError(f"Failed to make prediction: {str(e)}")
    
    def _calculate_success_probability(self, performance_ratio: float) -> float:
        """
        Calculate the probability of success based on performance ratio.
        
        Args:
            performance_ratio: Ratio of expected performance to target
            
        Returns:
            Probability between 0 and 1
        """
        # Simplified calculation - could be more sophisticated in a real model
        # Using sigmoid function to map performance ratio to probability
        if performance_ratio <= 0:
            return 0.0
            
        prob = 1 / (1 + np.exp(-5 * (performance_ratio - 0.8)))
        return min(max(prob, 0.0), 1.0)
    
    def _generate_recommendation(
        self, 
        score: float, 
        expected_sales: float, 
        probability: float,
        location: StoreLocation
    ) -> str:
        """
        Generate a recommendation based on prediction results.
        
        Args:
            score: Prediction score (0-1)
            expected_sales: Expected monthly sales
            probability: Success probability
            location: Store location
            
        Returns:
            Recommendation text
        """
        if score >= 0.8:
            return (
                f"Esta ubicación tiene un excelente potencial para una tienda OXXO. "
                f"Las ventas mensuales esperadas de ${expected_sales:,.2f} están muy por "
                f"encima del objetivo para entornos de tipo '{location.entorno}', con una "
                f"probabilidad de éxito del {probability*100:.1f}%."
            )
        elif score >= 0.6:
            return (
                f"Esta ubicación muestra un buen potencial para una tienda OXXO. "
                f"Las ventas mensuales esperadas de ${expected_sales:,.2f} superan "
                f"el objetivo para entornos de tipo '{location.entorno}', con una "
                f"probabilidad de éxito del {probability*100:.1f}%."
            )
        elif score >= 0.4:
            return (
                f"Esta ubicación tiene un potencial moderado para una tienda OXXO. "
                f"Las ventas mensuales esperadas de ${expected_sales:,.2f} están cerca "
                f"del objetivo para entornos de tipo '{location.entorno}', con una "
                f"probabilidad de éxito del {probability*100:.1f}%."
            )
        else:
            return (
                f"Esta ubicación muestra un bajo potencial para una tienda OXXO. "
                f"Las ventas mensuales esperadas de ${expected_sales:,.2f} están por debajo "
                f"del objetivo para entornos de tipo '{location.entorno}', con una "
                f"probabilidad de éxito del {probability*100:.1f}%. Recomendamos considerar "
                f"ubicaciones alternativas."
            )
    
    def get_optimal_locations(self, area: AreaRequest) -> List[StoreLocation]:
        """
        Find optimal store locations within a specified area.
        
        Args:
            area: Area request with center coordinates and radius
            
        Returns:
            List of optimal store locations
        """
        try:
            # Get existing stores in the area
            existing_stores = self.data_service.get_stores_in_area(
                area.lat, area.lng, area.radius
            )
            
            # If no existing stores, return empty list
            if not existing_stores:
                return []
            
            # Predict performance for all existing stores
            store_scores = []
            for store in existing_stores:
                prediction = self.predict_location(store)
                store_scores.append((store, prediction.score))
            
            # Sort by score in descending order
            store_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top 5 stores
            top_stores = [store for store, _ in store_scores[:5]]
            
            return top_stores
            
        except Exception as e:
            logger.error(f"Error finding optimal locations: {str(e)}")
            raise ValueError(f"Failed to find optimal locations: {str(e)}")
    
    def analyze_location(self, location: StoreLocation) -> LocationAnalysisResult:
        """
        Perform detailed analysis of a store location.
        
        Args:
            location: Store location to analyze
            
        Returns:
            LocationAnalysisResult with detailed analysis
        """
        try:
            # Get basic prediction
            prediction = self.predict_location(location)
            
            # Get nearby stores
            nearby_stores = self.data_service.get_stores_in_area(
                location.latitud, location.longitud, 2.0  # 2km radius
            )
            
            # Generate sales forecast
            sales_forecast = self._generate_sales_forecast(
                location, prediction.expectedSales
            )
            
            # Create analysis result
            result = LocationAnalysisResult(
                location=location,
                prediction=prediction,
                nearbyStores=nearby_stores if nearby_stores else None,
                salesForecast=sales_forecast
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing location: {str(e)}")
            raise ValueError(f"Failed to analyze location: {str(e)}")
    
    def _generate_sales_forecast(
        self, 
        location: StoreLocation, 
        base_sales: float
    ) -> List[SalesForecast]:
        """
        Generate a sales forecast for the next 6 months.
        
        Args:
            location: Store location
            base_sales: Base monthly sales
            
        Returns:
            List of SalesForecast objects
        """
        # Current month
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Seasonal factors - simplified model
        # In a real application, these would be derived from historical data
        seasonal_factors = {
            1: 0.85,  # January
            2: 0.90,  # February
            3: 0.95,  # March
            4: 1.00,  # April
            5: 1.05,  # May
            6: 1.10,  # June
            7: 1.15,  # July
            8: 1.10,  # August
            9: 1.05,  # September
            10: 1.00,  # October
            11: 1.10,  # November
            12: 1.20,  # December
        }
        
        # Generate forecast for next 6 months
        forecast = []
        for i in range(6):
            # Calculate month and year
            month = (current_month + i) % 12
            if month == 0:
                month = 12
            year = current_year + (current_month + i - 1) // 12
            
            # Apply seasonal factor
            seasonal_factor = seasonal_factors[month]
            monthly_sales = base_sales * seasonal_factor
            
            # Add random noise (±5%)
            noise = np.random.uniform(-0.05, 0.05)
            monthly_sales *= (1 + noise)
            
            # Create forecast entry
            month_id = f"{year}{month:02d}"
            forecast.append(SalesForecast(
                month=month_id,
                amount=monthly_sales
            ))
        
        return forecast
    
    def generate_heatmap(self, bounds: MapBounds) -> HeatmapData:
        """
        Generate a heatmap of store location quality within geographic bounds.
        
        Args:
            bounds: Geographic boundaries
            
        Returns:
            HeatmapData with points and center coordinates
        """
        try:
            # Calculate center
            center_lat = (bounds.north + bounds.south) / 2
            center_lng = (bounds.east + bounds.west) / 2
            
            # Get existing stores in the area
            # Calculate radius (approximate conversion from degrees to km)
            lat_radius = (bounds.north - bounds.south) * 111 / 2  # 111 km per degree
            lng_radius = (bounds.east - bounds.west) * 111 / 2  # approximate
            radius_km = max(lat_radius, lng_radius) * 1.5  # Add 50% margin
            
            existing_stores = self.data_service.get_stores_in_area(
                center_lat, center_lng, radius_km
            )
            
            # If no existing stores, generate a basic grid
            if not existing_stores:
                points = self._generate_grid_points(bounds)
            else:
                # Predict performance for all existing stores
                points = []
                for i, store in enumerate(existing_stores):
                    prediction = self.predict_location(store)
                    
                    # Determine color based on score
                    color = self._get_color_for_score(prediction.score)
                    
                    points.append(MapPoint(
                        id=f"store_{store.tiendaId or i}",
                        lat=store.latitud,
                        lng=store.longitud,
                        score=prediction.score,
                        color=color
                    ))
            
            # Create heatmap data
            heatmap_data = HeatmapData(
                points=points,
                centerLat=center_lat,
                centerLng=center_lng
            )
            
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {str(e)}")
            raise ValueError(f"Failed to generate heatmap: {str(e)}")
    
    def _generate_grid_points(self, bounds: MapBounds) -> List[MapPoint]:
        """
        Generate a grid of points within the given bounds.
        
        Args:
            bounds: Geographic boundaries
            
        Returns:
            List of MapPoint objects
        """
        # Number of points in each dimension
        n_lat = 10
        n_lng = 10
        
        # Generate grid
        lat_step = (bounds.north - bounds.south) / n_lat
        lng_step = (bounds.east - bounds.west) / n_lng
        
        points = []
        for i in range(n_lat):
            for j in range(n_lng):
                lat = bounds.south + (i + 0.5) * lat_step
                lng = bounds.west + (j + 0.5) * lng_step
                
                # Generate a random score for demonstration
                score = np.random.uniform(0.3, 0.9)
                
                # Determine color based on score
                color = self._get_color_for_score(score)
                
                points.append(MapPoint(
                    id=f"grid_{i}_{j}",
                    lat=lat,
                    lng=lng,
                    score=score,
                    color=color
                ))
        
        return points
    
    def _get_color_for_score(self, score: float) -> str:
        """
        Get a color hex code based on a score.
        
        Args:
            score: Score between 0 and 1
            
        Returns:
            Hex color code
        """
        if score >= 0.8:
            return "#10b981"  # Green
        elif score >= 0.6:
            return "#3b82f6"  # Blue
        elif score >= 0.4:
            return "#f59e0b"  # Yellow/Orange
        else:
            return "#ef4444"  # Red

