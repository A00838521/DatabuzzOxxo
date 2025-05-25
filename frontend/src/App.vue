<script setup lang="ts">
import StoreLocationPredictor from './components/StoreLocationPredictor.vue'
import './assets/main.css'
</script>

<template>
  <div class="app">
    <StoreLocationPredictor />
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>