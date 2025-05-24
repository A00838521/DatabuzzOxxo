<template>
  <div class="store-location-predictor">
    <div class="predictor-container">
      <div class="form-container">
        <form @submit.prevent="predictLocation">
          <div class="form-grid">
            <div class="form-group">
              <label for="longitud">Longitud</label>
              <input 
                type="number" 
                id="longitud" 
                v-model.number="storeData.longitud" 
                step="0.00001" 
                required
              />
            </div>
            
            <div class="form-group">
              <label for="segmentoMaestro">Segmento Maestro</label>
              <select 
                id="segmentoMaestro" 
                v-model="storeData.segmentoMaestro" 
                required
              >
                <option value="Hogar Reunión">Hogar Reunión</option>
                <option value="Trabajo Reunión">Trabajo Reunión</option>
                <option value="Tránsito">Tránsito</option>
                <option value="Estación">Estación</option>
              </select>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="resetForm" class="secondary-button">Limpiar</button>
            <button type="submit" class="primary-button">Predecir</button>
          </div>
        </form>
      </div>
      
      <!-- Prediction Results -->
      <div class="results-container" v-if="predictionResult">
        <div class="result-card">
          <h3>Resultado de la Predicción</h3>
          
          <div class="score-indicator" :class="getScoreClass(predictionResult.score)">
            <div class="score-value">{{ Math.round(predictionResult.score * 100) }}</div>
            <div class="score-label">Puntaje</div>
          </div>
          
          <div class="result-details">
            <div class="result-item">
              <div class="label">Ventas Esperadas:</div>
              <div class="value">{{ formatCurrency(predictionResult.expectedSales) }}</div>
            </div>
            
            <div class="result-item">
              <div class="label">Probabilidad de Éxito:</div>
              <div class="value">{{ formatPercentage(predictionResult.probability) }}</div>
            </div>
            
            <div class="recommendation">
              <h4>Recomendación:</h4>
              <p>{{ predictionResult.recommendation }}</p>
            </div>
          </div>
          
          <div class="result-actions">
            <button @click="predictionResult = null" class="secondary-button">Volver al Formulario</button>
            <button @click="analyzeLocation" class="primary-button">Análisis Detallado</button>
          </div>
        </div>
      </div>
      
      <!-- Detailed Analysis Results (would be expanded in a real app) -->
      <div class="analysis-container" v-if="analysisResult">
        <div class="analysis-card">
          <!-- Analysis visualization would go here -->
          <h3>Análisis Detallado</h3>
          <p>Análisis completo para la ubicación seleccionada.</p>
          
          <div class="analysis-actions">
            <button @click="analysisResult = null" class="secondary-button">Cerrar Análisis</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { locationPredictionApi, type StoreLocation, type PredictionResponse, type LocationAnalysisResult } from '../services/api';

// State
const loading = ref(false);
const error = ref<string | null>(null);
const predictionResult = ref<PredictionResponse | null>(null);
const analysisResult = ref<LocationAnalysisResult | null>(null);

// Default store data
const defaultStoreData: StoreLocation = {
  plazaCve: 1,
  nivelSocioeconomico: 'C',
  entorno: 'Hogar',
  mts2Ventas: 100,
  puertasRefrig: 12,
  cajonesEstacionamiento: 0,
  latitud: 25.67,
  longitud: -100.22,
  segmentoMaestro: 'Hogar Reunión'
};

// Reactive store data
const storeData = reactive<StoreLocation>({ ...defaultStoreData });

// Reset form to default values
const resetForm = () => {
  error.value = null;
  predictionResult.value = null;
  analysisResult.value = null;
  
  // Reset all form fields to default values
  Object.assign(storeData, defaultStoreData);
};

// Make prediction API call
const predictLocation = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await locationPredictionApi.predictLocation(storeData);
    predictionResult.value = result;
  } catch (err) {
    console.error('Prediction error:', err);
    error.value = 'Error al procesar la predicción. Por favor intente de nuevo.';
  } finally {
    loading.value = false;
  }
};

// Request detailed analysis
const analyzeLocation = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await locationPredictionApi.analyzeLocation(storeData);
    analysisResult.value = result;
  } catch (err) {
    console.error('Analysis error:', err);
    error.value = 'Error al analizar la ubicación. Por favor intente de nuevo.';
  } finally {
    loading.value = false;
  }
};

// Helper function to determine score color class
const getScoreClass = (score: number): string => {
  if (score >= 0.8) return 'excellent';
  if (score >= 0.6) return 'good';
  if (score >= 0.4) return 'average';
  return 'poor';
};

// Formatters
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
  }).format(value);
};

const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value);
};
</script>

<style scoped>
.store-location-predictor {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.store-location-predictor h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 24px;
}

.predictor-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-container, .results-container, .analysis-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--color-text-secondary);
}

.form-group input, .form-group select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.primary-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.primary-button:hover {
  background-color: var(--color-primary-dark);
}

.secondary-button {
  background-color: white;
  color: var(--color-text);
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.secondary-button:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.result-card, .analysis-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-card h3, .analysis-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--color-heading);
  align-self: flex-start;
}

.score-indicator {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
  color: white;
}

.score-indicator.excellent {
  background-color: #10b981;
}

.score-indicator.good {
  background-color: #3b82f6;
}

.score-indicator.average {
  background-color: #f59e0b;
}

.score-indicator.poor {
  background-color: #ef4444;
}

.score-value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  margin-top: 4px;
}

.result-details {
  width: 100%;
  margin-bottom: 24px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.result-item .label {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.result-item .value {
  font-weight: 600;
}

.recommendation {
  background-color: #f8fafc;
  padding: 16px;
  border-radius: 4px;
  margin-top: 16px;
}

.recommendation h4 {
  font-size: 16px;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 8px;
  color: var(--color-heading);
}

.recommendation p {
  margin: 0;
  line-height: 1.5;
}

.result-actions, .analysis-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
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

.error-message {
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 16px;
  margin: 24px 0;
  color: #b91c1c;
  border-radius: 4px;
}

/* Responsive styles */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>

