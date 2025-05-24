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

export default api;

