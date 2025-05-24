<template>
  <div class="traffic-flow-chart">
    <h4>Patrones de Tráfico y Flujo de Clientes</h4>
    
    <div class="charts-grid">
      <div class="chart-section">
        <h5>Tráfico por Hora del Día</h5>
        <div class="line-chart" ref="hourlyChart"></div>
      </div>
      
      <div class="chart-section">
        <h5>Tráfico por Día de la Semana</h5>
        <div class="bar-chart" ref="weeklyChart"></div>
      </div>
    </div>
    
    <div class="traffic-types">
      <div class="traffic-card">
        <div class="traffic-icon pedestrian"></div>
        <div class="traffic-info">
          <div class="traffic-value">{{ formatNumber(trafficData.pedestrian) }}</div>
          <div class="traffic-label">Peatonal</div>
        </div>
      </div>
      
      <div class="traffic-card">
        <div class="traffic-icon vehicular"></div>
        <div class="traffic-info">
          <div class="traffic-value">{{ formatNumber(trafficData.vehicular) }}</div>
          <div class="traffic-label">Vehicular</div>
        </div>
      </div>
      
      <div class="traffic-card">
        <div class="traffic-icon public-transport"></div>
        <div class="traffic-info">
          <div class="traffic-value">{{ formatNumber(trafficData.publicTransport) }}</div>
          <div class="traffic-label">Transporte Público</div>
        </div>
      </div>
    </div>
    
    <div class="traffic-insights">
      <h5>Insights de Tráfico</h5>
      <ul class="insights-list">
        <li>Horas pico: {{ getPeakHours() }}</li>
        <li>Días de mayor actividad: {{ getPeakDays() }}</li>
        <li>Tráfico total diario promedio: {{ calculateAverageDailyTraffic() }}</li>
        <li>Proporción peatonal vs vehicular: {{ calculatePedestrianVehicularRatio() }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { type TrafficData } from '../../services/api';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { 
  TitleComponent, 
  TooltipComponent, 
  GridComponent,
  DataZoomComponent,
  LegendComponent 
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// Register ECharts components
echarts.use([
  TitleComponent, 
  TooltipComponent, 
  GridComponent, 
  DataZoomComponent,
  LegendComponent,
  LineChart,
  BarChart,
  CanvasRenderer
]);

const props = defineProps<{
  trafficData: TrafficData;
}>();

const hourlyChart = ref<HTMLElement | null>(null);
const weeklyChart = ref<HTMLElement | null>(null);
let hourlyChartInstance: echarts.ECharts | null = null;
let weeklyChartInstance: echarts.ECharts | null = null;

// Helper functions
const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-MX').format(value);
};

const getPeakHours = (): string => {
  // Sort hours by volume and get top 2
  const peakHours = [...props.trafficData.hourly]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 2)
    .map(item => {
      const hour = item.hour;
      return `${hour}:00 - ${hour + 1}:00`;
    })
    .join(' y ');
  
  return peakHours;
};

const getPeakDays = (): string => {
  // Sort days by volume and get top 2
  const daysMap: Record<string, string> = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
  };
  
  const peakDays = [...props.trafficData.weekly]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 2)
    .map(item => daysMap[item.day] || item.day)
    .join(' y ');
  
  return peakDays;
};

const calculateAverageDailyTraffic = (): string => {
  const

