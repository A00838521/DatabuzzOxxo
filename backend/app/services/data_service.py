import pandas as pd
import numpy as np
import os
from typing import List, Dict, Optional, Tuple, Any, Union
import logging
from functools import lru_cache
from datetime import datetime
import json
from pathlib import Path

from app.models.location import StoreLocation

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataService:
    """
    Service for handling data operations related to OXXO store locations
    and sales data.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data service with paths to data files.
        
        Args:
            data_path: Optional path to the data directory. If not provided,
                      will use the default path.
        """
        self.data_path = data_path or os.path.join(
            os.path.expanduser("~"), 
            "Downloads", 
            "Reto Oxxo"
        )
        logger.info(f"Data path set to: {self.data_path}")
        
        # Paths to data files
        self.store_data_path = os.path.join(self.data_path, "DIM_TIENDA.csv")
        self.test_store_data_path = os.path.join(self.data_path, "DIM_TIENDA_TEST.csv")
        self.sales_data_path = os.path.join(self.data_path, "Venta.csv")
        self.sales_target_path = os.path.join(self.data_path, "Meta_venta.csv")
        
        # Data frames
        self._stores_df = None
        self._test_stores_df = None
        self._sales_df = None
        self._sales_target_df = None
        
        # Feature names mapping
        self.feature_mapping = {
            'TIENDA_ID': 'tiendaId',
            'PLAZA_CVE': 'plazaCve',
            'NIVELSOCIOECONOMICO_DES': 'nivelSocioeconomico',
            'ENTORNO_DES': 'entorno',
            'MTS2VENTAS_NUM': 'mts2Ventas',
            'PUERTASREFRIG_NUM': 'puertasRefrig',
            'CAJONESESTACIONAMIENTO_NUM': 'cajonesEstacionamiento',
            'LATITUD_NUM': 'latitud',
            'LONGITUD_NUM': 'longitud',
            'SEGMENTO_MAESTRO_DESC': 'segmentoMaestro',
        }
        
        # Load data
        self.load_data()
    
    def load_data(self) -> None:
        """
        Load all data files and preprocess them.
        """
        try:
            logger.info("Loading store data...")
            self._stores_df = pd.read_csv(self.store_data_path)
            self._stores_df = self._preprocess_store_data(self._stores_df)
            
            logger.info("Loading test store data...")
            self._test_stores_df = pd.read_csv(self.test_store_data_path)
            self._test_stores_df = self._preprocess_store_data(self._test_stores_df)
            
            logger.info("Loading sales data...")
            self._sales_df = pd.read_csv(self.sales_data_path)
            self._sales_df = self._preprocess_sales_data(self._sales_df)
            
            logger.info("Loading sales target data...")
            self._sales_target_df = pd.read_csv(self.sales_target_path)
            
            # Create a combined dataframe for training
            self._create_combined_dataset()
            
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise ValueError(f"Failed to load data: {str(e)}")
    
    def _preprocess_store_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess store data for analysis.
        
        Args:
            df: Raw store data DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Convert column names to match our model
        df = df.rename(columns=self.feature_mapping)
        
        # Handle missing values
        df = df.assign(cajonesEstacionamiento=df['cajonesEstacionamiento'].fillna(0))
        
        # Remove any rows with missing critical data
        critical_columns = ['plazaCve', 'nivelSocioeconomico', 'entorno', 
                           'mts2Ventas', 'latitud', 'longitud']
        df = df.dropna(subset=critical_columns)
        
        # Remove duplicate stores
        df = df.drop_duplicates(subset=['tiendaId'], keep='first')
        
        # Ensure correct data types
        df['tiendaId'] = df['tiendaId'].astype(int)
        df['plazaCve'] = df['plazaCve'].astype(int)
        df['puertasRefrig'] = df['puertasRefrig'].astype(int)
        df['cajonesEstacionamiento'] = df['cajonesEstacionamiento'].astype(int)
        
        return df
    
    def _preprocess_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess sales data for analysis.
        
        Args:
            df: Raw sales data DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Convert TIENDA_ID to int
        df['TIENDA_ID'] = df['TIENDA_ID'].astype(int)
        
        # Convert MES_ID to period
        df['MES_ID'] = df['MES_ID'].astype(str)
        
        # Sort by store and month
        df = df.sort_values(['TIENDA_ID', 'MES_ID'])
        
        return df
    
    def _create_combined_dataset(self) -> None:
        """
        Create a combined dataset with store data and sales data
        for model training.
        """
        try:
            # Merge store data with sales data
            self._combined_df = pd.merge(
                self._stores_df,
                self._sales_df,
                left_on='tiendaId',
                right_on='TIENDA_ID',
                how='inner'
            )
            
            # Merge with sales targets
            self._combined_df = pd.merge(
                self._combined_df,
                self._sales_target_df,
                left_on='entorno',
                right_on='ENTORNO_DES',
                how='left'
            )
            
            # Clean up the combined dataframe
            self._combined_df.drop(['TIENDA_ID', 'ENTORNO_DES'], axis=1, inplace=True)
            
            logger.info(f"Combined dataset created with {len(self._combined_df)} records")
        except Exception as e:
            logger.error(f"Error creating combined dataset: {str(e)}")
            raise ValueError(f"Failed to create combined dataset: {str(e)}")
    
    @lru_cache(maxsize=128)
    def get_store_by_id(self, store_id: int) -> Optional[StoreLocation]:
        """
        Get store data by ID.
        
        Args:
            store_id: The ID of the store to retrieve
            
        Returns:
            StoreLocation object if found, None otherwise
        """
        try:
            # Try to find in training data
            store_row = self._stores_df[self._stores_df['tiendaId'] == store_id]
            
            if len(store_row) == 0:
                # Try to find in test data
                store_row = self._test_stores_df[self._test_stores_df['tiendaId'] == store_id]
            
            if len(store_row) == 0:
                return None
            
            # Convert to dictionary and then to StoreLocation
            store_dict = store_row.iloc[0].to_dict()
            
            # Remove any columns not in our model
            store_dict = {k: v for k, v in store_dict.items() 
                         if k in StoreLocation.__annotations__}
            
            return StoreLocation(**store_dict)
        except Exception as e:
            logger.error(f"Error retrieving store {store_id}: {str(e)}")
            return None
    
    def get_all_stores(self) -> List[StoreLocation]:
        """
        Get all stores from both training and test datasets.
        
        Returns:
            List of StoreLocation objects
        """
        try:
            # Combine training and test data
            all_stores_df = pd.concat([self._stores_df, self._test_stores_df])
            
            # Convert to list of dictionaries
            store_dicts = all_stores_df.to_dict(orient='records')
            
            # Convert to StoreLocation objects
            store_locations = []
            for store_dict in store_dicts:
                # Filter to only include columns in our model
                filtered_dict = {k: v for k, v in store_dict.items() 
                               if k in StoreLocation.__annotations__}
                store_locations.append(StoreLocation(**filtered_dict))
            
            return store_locations
        except Exception as e:
            logger.error(f"Error retrieving all stores: {str(e)}")
            return []
    
    def get_stores_in_area(self, lat: float, lng: float, radius_km: float) -> List[StoreLocation]:
        """
        Get stores within a specified radius of a location.
        
        Args:
            lat: Latitude of the center point
            lng: Longitude of the center point
            radius_km: Radius in kilometers
            
        Returns:
            List of StoreLocation objects within the radius
        """
        try:
            # Combine training and test data
            all_stores_df = pd.concat([self._stores_df, self._test_stores_df])
            
            # Calculate distance using Haversine formula
            # First convert latitude and longitude from degrees to radians
            lat_rad = np.radians(lat)
            lng_rad = np.radians(lng)
            all_stores_df['lat_rad'] = np.radians(all_stores_df['latitud'])
            all_stores_df['lng_rad'] = np.radians(all_stores_df['longitud'])
            
            # Haversine formula
            all_stores_df['dlon'] = all_stores_df['lng_rad'] - lng_rad
            all_stores_df['dlat'] = all_stores_df['lat_rad'] - lat_rad
            all_stores_df['a'] = np.sin(all_stores_df['dlat']/2)**2 + \
                                np.cos(lat_rad) * np.cos(all_stores_df['lat_rad']) * \
                                np.sin(all_stores_df['dlon']/2)**2
            all_stores_df['c'] = 2 * np.arcsin(np.sqrt(all_stores_df['a']))
            all_stores_df['distance_km'] = 6371 * all_stores_df['c']  # Earth radius in km
            
            # Filter stores within radius
            nearby_stores_df = all_stores_df[all_stores_df['distance_km'] <= radius_km]
            
            # Sort by distance
            nearby_stores_df = nearby_stores_df.sort_values('distance_km')
            
            # Drop temporary columns
            nearby_stores_df = nearby_stores_df.drop(
                ['lat_rad', 'lng_rad', 'dlon', 'dlat', 'a', 'c', 'distance_km'], 
                axis=1
            )
            
            # Convert to list of dictionaries
            store_dicts = nearby_stores_df.to_dict(orient='records')
            
            # Convert to StoreLocation objects
            store_locations = []
            for store_dict in store_dicts:
                # Filter to only include columns in our model
                filtered_dict = {k: v for k, v in store_dict.items() 
                               if k in StoreLocation.__annotations__}
                store_locations.append(StoreLocation(**filtered_dict))
            
            return store_locations
        except Exception as e:
            logger.error(f"Error retrieving stores in area: {str(e)}")
            return []
    
    def get_sales_for_store(self, store_id: int) -> Dict[str, float]:
        """
        Get sales data for a specific store.
        
        Args:
            store_id: ID of the store
            
        Returns:
            Dictionary mapping months to sales figures
        """
        try:
            # Filter sales data for this store
            store_sales = self._sales_df[self._sales_df['TIENDA_ID'] == store_id]
            
            if len(store_sales) == 0:
                return {}
            
            # Create a dictionary of month to sales
            sales_dict = dict(zip(store_sales['MES_ID'], store_sales['VENTA_TOTAL']))
            
            return sales_dict
        except Exception as e:
            logger.error(f"Error retrieving sales for store {store_id}: {str(e)}")
            return {}
    
    def get_sales_target_for_environment(self, environment: str) -> Optional[float]:
        """
        Get the sales target for a specific environment type.
        
        Args:
            environment: Environment type (e.g., 'Base', 'Hogar')
            
        Returns:
            Sales target value or None if not found
        """
        try:
            # Filter sales target data for this environment
            target_row = self._sales_target_df[self._sales_target_df['ENTORNO_DES'] == environment]
            
            if len(target_row) == 0:
                return None
            
            # Get the target value
            target_value = target_row.iloc[0]['Meta_venta']
            
            return float(target_value)
        except Exception as e:
            logger.error(f"Error retrieving sales target for environment {environment}: {str(e)}")
            return None
    
    def get_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Get the training data for the prediction model.
        
        Returns:
            Tuple of (X, y) where X is the feature DataFrame and y is the target Series
        """
        try:
            # Create a copy of the combined dataframe
            df = self._combined_df.copy()
            
            # Create a performance metric (ratio of actual sales to target)
            df['performance_ratio'] = df['VENTA_TOTAL'] / df['Meta_venta']
            
            # Select features for training
            X = df[[
                'plazaCve', 
                'mts2Ventas', 
                'puertasRefrig', 
                'cajonesEstacionamiento',
                'latitud',
                'longitud'
            ]]
            
            # Add one-hot encoded categorical variables
            X_categorical = pd.get_dummies(
                df[['nivelSocioeconomico', 'entorno', 'segmentoMaestro']], 
                drop_first=True
            )
            
            # Combine numerical and categorical features
            X = pd.concat([X, X_categorical], axis=1)
            
            # Target variable
            y = df['performance_ratio']
            
            return X, y
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            raise ValueError(f"Failed to prepare training data: {str(e)}")
    
    def store_location_to_features(self, location: StoreLocation) -> pd.DataFrame:
        """
        Convert a StoreLocation model to a DataFrame with the same
        feature format as the training data.
        
        Args:
            location: StoreLocation object
            
        Returns:
            DataFrame with features for prediction
        """
        try:
            # Get the training data to see the exact feature order
            X_train, _ = self.get_training_data()
            feature_order = X_train.columns.tolist()
            
            # Define all possible categories for each categorical variable
            nivel_cats = ['A', 'AB', 'B', 'BC', 'C', 'CD', 'D']
            entorno_cats = ['Base', 'Hogar', 'Peatonal', 'Receso']
            segmento_cats = ['Barrio Competido', 'Clásico', 'Hogar Reunión', 'Oficinistas', 'Parada Técnica']
            
            # Create a dictionary from the location
            location_dict = location.dict()
            
            # Create a DataFrame with one row
            df = pd.DataFrame([location_dict])
            
            # Select numerical features
            X = df[[
                'plazaCve', 
                'mts2Ventas', 
                'puertasRefrig', 
                'cajonesEstacionamiento',
                'latitud',
                'longitud'
            ]]
            
            # Create dummy variables for each categorical variable separately
            # Using specific categories to ensure consistent output
            nivel_dummies = pd.get_dummies(df['nivelSocioeconomico'], prefix='nivelSocioeconomico')
            entorno_dummies = pd.get_dummies(df['entorno'], prefix='entorno')
            segmento_dummies = pd.get_dummies(df['segmentoMaestro'], prefix='segmentoMaestro')
            
            # Add any missing columns with zero values
            for cat in nivel_cats:
                col_name = f'nivelSocioeconomico_{cat}'
                if col_name not in nivel_dummies.columns:
                    nivel_dummies[col_name] = 0
                    
            for cat in entorno_cats:
                col_name = f'entorno_{cat}'
                if col_name not in entorno_dummies.columns:
                    entorno_dummies[col_name] = 0
                    
            for cat in segmento_cats:
                col_name = f'segmentoMaestro_{cat}'
                if col_name not in segmento_dummies.columns:
                    segmento_dummies[col_name] = 0
            
            # Combine all features first to have all possible columns
            X = pd.concat([X, nivel_dummies, entorno_dummies, segmento_dummies], axis=1)
            
            # Ensure we have all necessary columns from training
            for col in feature_order:
                if col not in X.columns:
                    X[col] = 0
                    
            # Reorder columns to match exact training order
            X = X[feature_order]
            
            return X
        except Exception as e:
            logger.error(f"Error converting StoreLocation to features: {str(e)}")
            raise ValueError(f"Failed to convert StoreLocation to features: {str(e)}")
    
    def get_average_sales_by_environment(self) -> Dict[str, float]:
        """
        Get the average sales by environment type.
        
        Returns:
            Dictionary mapping environment types to average sales
        """
        try:
            # Create a copy of the combined dataframe
            df = self._combined_df.copy()
            
            # Group by environment and calculate mean sales
            avg_sales = df.groupby('entorno')['VENTA_TOTAL'].mean().to_dict()
            
            return avg_sales
        except Exception as e:
            logger.error(f"Error calculating average sales by environment: {str(e)}")
            return {}
    
    def save_prediction_log(self, location: StoreLocation, prediction: Dict[str, Any]) -> None:
        """
        Save prediction log for future analysis.
        
        Args:
            location: StoreLocation that was analyzed
            prediction: Prediction results
        """
        try:
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(self.data_path, 'prediction_logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            # Prepare log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'location': location.dict(),
                'prediction': prediction
            }
            
            # Generate filename based on timestamp
            filename = f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(logs_dir, filename)
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(log_entry, f, indent=2)
                
            logger.info(f"Prediction log saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving prediction log: {str(e)}")
            # Don't raise exception here since this is not critical

