<template>
  <div class="economic-zone-analysis">
    <h4>Análisis de Zona Económica</h4>
    
    <div class="zone-info">
      <div class="zone-type" :class="getZoneTypeClass()">{{ economicZone.zoneType }}</div>
      
      <div class="indicators">
        <div class="indicator-card">
          <div class="indicator-value">{{ formatPercentage(economicZone.growthRate) }}</div>
          <div class="indicator-label">Tasa de Crecimiento</div>
        </div>
        
        <div class="indicator-card">
          <div class="indicator-value">{{ formatNumber(economicZone.businessCount) }}</div>
          <div class="indicator-label">Negocios en la Zona</div>
        </div>
        
        <div class="indicator-card">
          <div class="indicator-value">{{ formatCurrency(economicZone.averageIncome) }}</div>
          <div class="indicator-label">Ingreso Promedio</div>
        </div>
      </div>
    </div>
    
    <div class="score-section">
      <h5>Índices de Desarrollo</h5>
      <div class="score-container">
        <div class="score-item">
          <div class="score-label">Índice de Desarrollo</div>
          <div class="score-bar">
            <div 
              class="score-fill" 
              :style="{ width: `${economicZone.developmentIndex * 100}%` }"
              :class="getScoreClass(economicZone.developmentIndex)"
            ></div>
          </div>
          <div class="score-value">{{ formatPercentage(economicZone.developmentIndex) }}</div>
        </div>
        
        <div class="score-item">
          <div class="score-label">Estabilidad Económica</div>
          <div class="score-bar">
            <div 
              class="score-fill" 
              :style="{ width: `${economicZone.stabilityScore * 100}%` }"
              :class="getScoreClass(economicZone.stabilityScore)"
            ></div>
          </div>
          <div class="score-value">{{ formatPercentage(economicZone.stabilityScore) }}</div>
        </div>
      </div>
    </div>
    
    <div class="sector-analysis">
      <h5>Presencia de Sectores Económicos</h5>
      <div class="sector-chart" ref="sectorChart"></div>
    </div>
    
    <div class="business-density">
      <h5>Densidad de Negocios</h5>
      <div class="business-chart" ref="businessChart"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { type EconomicZoneData } from '../../services/api';
import * as echarts from 'echarts/core';
import { RadarChart, BarChart } from 'echarts/charts';
import { 
  TitleComponent, 
  TooltipComponent, 
  LegendComponent,
  GridComponent 
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// Register ECharts components
echarts.use([
  TitleComponent, 
  TooltipComponent, 
  LegendComponent,
  GridComponent,
  RadarChart, 
  BarChart,
  CanvasRenderer
]);

const props = defineProps<{
  economicZone: EconomicZoneData;
}>();

const sectorChart = ref<HTMLElement | null>(null);
const businessChart = ref<HTMLElement | null>(null);
let sectorChartInstance: echarts.ECharts | null = null;
let businessChartInstance: echarts.ECharts | null = null;

// Helper functions
const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-MX').format(value);
};

const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value);
};

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    maximumFractionDigits: 0
  }).format(value);
};

const getZoneTypeClass = (): string => {
  const zoneType = props.economicZone.zoneType.toLowerCase();
  if (zoneType.includes('comercial')) return 'commercial';
  if (zoneType.includes('residencial')) return 'residential';
  if (zoneType.includes('industrial')) return 'industrial';
  if (zoneType.includes('mixto')) return 'mixed';
  return '';
};

const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent';
  if (score >= 0.6) return 'good';
  if (score >= 0.4) return 'average';
  return 'poor';
};

// Initialize charts
const initCharts = () => {
  if (sectorChart.value) {
    sectorChartInstance = echarts.init(sectorChart.value);
    
    // Extract data for radar chart
    const sectors = props.economicZone.sectors.map(sector => sector.name);
    const presenceValues = props.economicZone.sectors.map(sector => sector.presence);
    
    sectorChartInstance.setOption({
      tooltip: {
        trigger: 'item'
      },
      radar: {
        indicator: sectors.map(sector => ({ name: sector, max: 1 })),
        radius: '65%'
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: presenceValues,
              name: 'Presencia de Sectores',
              areaStyle: {
                color: 'rgba(59, 130, 246, 0.6)'
              },
              lineStyle: {
                color: '#3b82f6'
              },
              itemStyle: {
                color: '#3b82f6'
              }
            }
          ]
        }
      ]
    });
  }
  
  if (businessChart.value) {
    businessChartInstance = echarts.init(businessChart.value);
    
    // Create mock data for business density chart
    // In a real application, this would come from the backend
    const businessTypes = [
      'Tiendas de Conveniencia',
      'Restaurantes',
      'Comercio Minorista',
      'Servicios Profesionales',
      'Entretenimiento'
    ];
    
    const businessCounts = [
      Math.round(props.economicZone.businessCount * 0.15),  // 15% convenience stores
      Math.round(props.economicZone.businessCount * 0.25),  // 25% restaurants
      Math.round(props.economicZone.businessCount * 0.30),  // 30% retail
      Math.round(props.economicZone.businessCount * 0.20),  // 20% professional services
      Math.round(props.economicZone.businessCount * 0.10)   // 10% entertainment
    ];
    
    businessChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: businessTypes,
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: 'Número de Negocios'
      },
      series: [
        {
          data: businessCounts,
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            color: function(params: any) {
              const colors = ['#10b981', '#3b82f6', '#f59e0b', '#6366f1', '#ef4444'];
              return colors[params.dataIndex];
            }
          }
        }
      ],
      grid: {
        left: '5%',
        right: '5%',
        bottom: '15%',
        top: '10%',
        containLabel: true
      }
    });
  }
};

// Handle window resize
const handleResize = () => {
  sectorChartInstance?.resize();
  businessChartInstance?.resize();
};

// Update charts when economic zone data changes
watch(() => props.economicZone, () => {
  if (sectorChartInstance) {
    const sectors = props.economicZone.sectors.map(sector => sector.name);
    const presenceValues = props.economicZone.sectors.map(sector => sector.presence);
    
    sectorChartInstance.setOption({
      radar: {
        indicator: sectors.map(sector => ({ name: sector, max: 1 }))
      },
      series: [
        {
          data: [
            {
              value: presenceValues
            }
          ]
        }
      ]
    });
  }
  
  if (businessChartInstance) {
    // Update with real data in a real implementation
    const businessCounts = [
      Math.round(props.economicZone.businessCount * 0.15),
      Math.round(props.economicZone.businessCount * 0.25),
      Math.round(props.economicZone.businessCount * 0.30),
      Math.round(props.economicZone.businessCount * 0.20),
      Math.round(props.economicZone.businessCount * 0.10)
    ];
    
    businessChartInstance.setOption({
      series: [
        {
          data: businessCounts
        }
      ]
    });
  }
}, { deep: true });

// Lifecycle hooks
onMounted(() => {
  initCharts();
  window.addEventListener('resize', handleResize);
});

const onBeforeUnmount = () => {
  window.removeEventListener('resize', handleResize);
  sectorChartInstance?.dispose();
  businessChartInstance?.dispose();
};
</script>

<style scoped>
.economic-zone-analysis {
  width: 100%;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.economic-zone-analysis h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--color-heading);
}

.economic-zone-analysis h5 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
  color: var(--color-text-secondary);
}

.zone-info {
  margin-bottom: 20px;
}

.zone-type {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 600;
  margin-bottom: 16px;
  color: white;
}

.zone-type.commercial {
  background-color: #3b82f6;
}

.zone-type.residential {
  background-color: #10b981;
}

.zone-type.industrial {
  background-color: #ef4444;
}

.zone-type.mixed {
  background-color: #f59e0b;
}

.indicators {
  display: flex;
  gap: 16px;
}

.indicator-card {
  flex: 1;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 6px;
  text-align: center;
}

.indicator-value {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--color-primary);
}

.indicator-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.score-section {
  margin-bottom: 20px;
}

.score-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  width: 170px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.score-bar {
  flex: 1;
  height: 12px;
  background-color: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 6px;
}

.score-fill.excellent {
  background-color: #10b981;
}

.score-fill.good {
  background-color: #3b82f6;
}

.score-fill.average {
  background-color: #f59e0b;
}

.score-fill.poor {
  background-color: #ef4444;
}

.score-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 500;
}

.sector-analysis, .business-density {
  margin-bottom: 20px;
}

.sector-chart,

