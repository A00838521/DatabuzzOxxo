<template>
  <div class="metric-card">
    <div class="metric-header">
      <h3>{{ title }}</h3>
      <span class="icon" v-if="icon">{{ icon }}</span>
    </div>
    <div class="metric-value">{{ value }}</div>
    <div v-if="trend" class="metric-trend" :class="{ positive: trend.isPositive }">
      {{ trend.value }}%
      <span class="trend-arrow">{{ trend.isPositive ? '↑' : '↓' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MetricCard } from '../types/dashboard';

defineProps<MetricCard>();
</script>

<style scoped>
.metric-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-header h3 {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.metric-trend {
  font-size: 0.875rem;
  color: #dc2626;
}

.metric-trend.positive {
  color: #16a34a;
}

.trend-arrow {
  margin-left: 0.25rem;
}
</style>

