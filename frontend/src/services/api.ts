import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SalesData {
  date: string;
  amount: number;
  category: string;
}

export interface StoreMetrics {
  totalSales: number;
  averageTicket: number;
  topCategories: { category: string; sales: number }[];
}

export interface StoreLocation {
  tiendaId?: number;
  plazaCve: number;
  nivelSocioeconomico: string;
  entorno: string;
  mts2Ventas: number;
  puertasRefrig: number;
  cajonesEstacionamiento: number;
  latitud: number;
  longitud: number;
  segmentoMaestro: string;
}

export interface PredictionResponse {
  score: number;
  expectedSales: number;
  probability: number;
  recommendation: string;
}

export interface LocationAnalysisResult {
  location: StoreLocation;
  prediction: PredictionResponse;
  nearbyStores?: StoreLocation[];
  salesForecast?: { month: string; amount: number }[];
}

export interface MapPoint {
  id: string;
  lat: number;
  lng: number;
  score: number;
  color: string;
}

export interface HeatmapData {
  points: MapPoint[];
  centerLat: number;
  centerLng: number;
}

export const dashboardApi = {
  async getSalesData(): Promise<SalesData[]> {
    const response = await api.get('/sales');
    return response.data;
  },
  
  async getStoreMetrics(): Promise<StoreMetrics> {
    const response = await api.get('/metrics');
    return response.data;
  }
};

export const locationPredictionApi = {
  async predictLocation(location: StoreLocation): Promise<PredictionResponse> {
    const response = await api.post('/predict-location', location);
    return response.data;
  },
  
  async getOptimalLocations(area: { lat: number; lng: number; radius: number }): Promise<StoreLocation[]> {
    const response = await api.post('/optimal-locations', area);
    return response.data;
  },
  
  async analyzeLocation(location: StoreLocation): Promise<LocationAnalysisResult> {
    const response = await api.post('/analyze-location', location);
    return response.data;
  },
  
  async getHeatmapData(bounds: { 
    north: number; 
    south: number; 
    east: number; 
    west: number 
  }): Promise<HeatmapData> {
    const response = await api.post('/location-heatmap', bounds);
    return response.data;
  },
  
  async getExistingStores(): Promise<StoreLocation[]> {
    const response = await api.get('/stores');
    return response.data;
  }
};

export default api;

