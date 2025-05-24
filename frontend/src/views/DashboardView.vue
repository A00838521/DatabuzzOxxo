<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard Databuzz Oxxo</h1>
      <div class="period-selector">
        <button 
          :class="{ active: selectedPeriod === 'daily' }" 
          @click="changePeriod('daily')"
        >
          Diario
        </button>
        <button 
          :class="{ active: selectedPeriod === 'weekly' }" 
          @click="changePeriod('weekly')"
        >
          Semanal
        </button>
        <button 
          :class="{ active: selectedPeriod === 'monthly' }" 
          @click="changePeriod('monthly')"
        >
          Mensual
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>Cargando datos...</p>
    </div>

    <template v-else>
      <!-- Metrics Row -->
      <div class="metrics-row">
        <MetricCard
          title="Ventas Totales"
          :value="formatCurrency(metrics.totalSales)"
          icon="📈"
          :trend="{ value: 12.5, isPositive: true }"
        />
        <MetricCard
          title="Ticket Promedio"
          :value="formatCurrency(metrics.averageTicket)"
          icon="🧾"
          :trend="{ value: 3.2, isPositive: true }"
        />
        <MetricCard
          title="Clientes"
          :value="formatNumber(1245)"
          icon="👥"
          :trend="{ value: 5.7, isPositive: true }"
        />
        <MetricCard
          title="Categorías Top"
          :value="metrics.topCategories.length > 0 ? metrics.topCategories[0].category : 'N/A'"
          icon="🏆"
        />
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <div class="chart-container wide">
          <h2>Tendencia de Ventas</h2>
          <LineChart :chartData="salesTrendData" />
        </div>
        
        <div class="chart-container">
          <h2>Ventas por Categoría</h2>
          <BarChart :chartData="categorySalesData" />
        </div>
        
        <div class="chart-container">
          <h2>Distribución por Día</h2>
          <BarChart :chartData="dailyDistributionData" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { dashboardApi, type SalesData, type StoreMetrics } from '../services/api';
import MetricCard from '../components/MetricCard.vue';
import LineChart from '../components/charts/LineChart.vue';
import BarChart from '../components/charts/BarChart.vue';
import type { ChartData } from '../types/dashboard';

// State
const loading = ref(true);
const salesData = ref<SalesData[]>([]);
const metrics = ref<StoreMetrics>({
  totalSales: 0,
  averageTicket: 0,
  topCategories: []
});
const selectedPeriod = ref('monthly');

// Fetch data
const fetchData = async () => {
  loading.value = true;
  try {
    // In a real application, we would use Promise.all for parallel requests
    const [salesResponse, metricsResponse] = await Promise.all([
      dashboardApi.getSalesData(),
      dashboardApi.getStoreMetrics()
    ]);
    
    salesData.value = salesResponse;
    metrics.value = metricsResponse;
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
    // In a production app, we would show an error message to the user
  } finally {
    loading.value = false;
  }
};

// Handle period change
const changePeriod = (period: string) => {
  selectedPeriod.value = period;
  fetchData();
};

// Formatters
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
  }).format(value);
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-MX').format(value);
};

// Computed chart data
// In a real application, these would transform the API data
// For now, we'll use mock data for demonstration

const salesTrendData = computed<ChartData>(() => {
  // Mock data when real data is not available
  if (salesData.value.length === 0) {
    return {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Ventas',
          data: [30000, 35000, 28000, 32000, 40000, 38000],
          borderColor: '#42b883',
          backgroundColor: 'rgba(66, 184, 131, 0.2)',
          borderWidth: 2
        }
      ]
    };
  }

  // Process real data (simplified example)
  const months: string[] = [];
  const values: number[] = [];

  // Group data by month and sum values
  // This is a simplified example - in a real app, you'd need proper date processing
  salesData.value.forEach(sale => {
    const date = new Date(sale.date);
    const month = date.toLocaleString('default', { month: 'short' });
    
    const monthIndex = months.indexOf(month);
    if (monthIndex === -1) {
      months.push(month);
      values.push(sale.amount);
    } else {
      values[monthIndex] += sale.amount;
    }
  });

  return {
    labels: months,
    datasets: [
      {
        label: 'Ventas',
        data: values,
        borderColor: '#42b883',
        backgroundColor: 'rgba(66, 184, 131, 0.2)',
        borderWidth: 2
      }
    ]
  };
});

const categorySalesData = computed<ChartData>(() => {
  // Mock data when real data is not available
  if (!metrics.value.topCategories || metrics.value.topCategories.length === 0) {
    return {
      labels: ['Bebidas', 'Snacks', 'Alimentos', 'Servicios', 'Otros'],
      datasets: [
        {
          label: 'Ventas por Categoría',
          data: [12000, 9000, 7500, 5000, 3000],
          backgroundColor: [
            '#42b883', '#35495e', '#ff7e67', '#ffca3a', '#8ac926'
          ],
          borderWidth: 0
        }
      ]
    };
  }

  // Process real data
  const categories = metrics.value.topCategories.map(cat => cat.category);
  const sales = metrics.value.topCategories.map(cat => cat.sales);

  // Colors array - in a real app, you might want a more sophisticated color assignment
  const colors = ['#42b883', '#35495e', '#ff7e67', '#ffca3a', '#8ac926', '#1982c4', '#6a4c93'];

  return {
    labels: categories,
    datasets: [
      {
        label: 'Ventas por Categoría',
        data: sales,
        backgroundColor: colors.slice(0, categories.length),
        borderWidth: 0
      }
    ]
  };
});

const dailyDistributionData = computed<ChartData>(() => {
  // Mock data for daily distribution
  return {
    labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
    datasets: [
      {
        label: 'Ventas por Día',
        data: [4500, 5200, 4800, 5500, 7800, 8500, 6200],
        backgroundColor: '#35495e',
        borderWidth: 0
      }
    ]
  };
});

// Lifecycle
onMounted(fetchData);
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-heading);
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 8px;
}

.period-selector button {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.period-selector button.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chart-container h2 {
  font-size: 16px;
  margin-top: 0;
  margin-bottom: 16px;
  color: var(--color-text-secondary);
}

.chart-container.wide {
  grid-column: span 2;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container.wide {
    grid-column: auto;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .metrics-row {
    grid-template-columns: 1fr;
  }
}
</style>

