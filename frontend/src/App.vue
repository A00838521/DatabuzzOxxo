<script setup lang="ts">
import DashboardView from './views/DashboardView.vue'
import './assets/main.css'
</script>

<template>
  <div class="app">
    <div class="app-sidebar">
      <div class="sidebar-logo">
        <img src="./assets/vue.svg" alt="Logo" />
        <h2>Databuzz<span>Oxxo</span></h2>
      </div>
      
      <nav class="sidebar-nav">
        <a href="#" class="nav-item active">
          <span class="nav-icon">📊</span>
          <span class="nav-label">Dashboard</span>
        </a>
        <a href="#" class="nav-item">
          <span class="nav-icon">📈</span>
          <span class="nav-label">Ventas</span>
        </a>
        <a href="#" class="nav-item">
          <span class="nav-icon">🏪</span>
          <span class="nav-label">Tiendas</span>
        </a>
        <a href="#" class="nav-item">
          <span class="nav-icon">📦</span>
          <span class="nav-label">Productos</span>
        </a>
        <a href="#" class="nav-item">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">Configuración</span>
        </a>
      </nav>
    </div>
    
    <div class="app-content">
      <DashboardView />
    </div>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  min-height: 100vh;
}

.app-sidebar {
  width: 240px;
  background-color: white;
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-logo {
  padding: 24px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-logo img {
  width: 32px;
  height: 32px;
}

.sidebar-logo h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--color-heading);
}

.sidebar-logo span {
  color: var(--color-primary);
}

.sidebar-nav {
  padding: 24px 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  text-decoration: none;
  color: var(--color-text);
  gap: 12px;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: var(--color-bg-hover);
}

.nav-item.active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.app-content {
  flex: 1;
  background-color: var(--color-bg);
  overflow: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .app-sidebar {
    width: 64px;
  }
  
  .sidebar-logo h2 {
    display: none;
  }
  
  .nav-label {
    display: none;
  }
  
  .nav-icon {
    font-size: 20px;
  }
  
  .sidebar-logo {
    justify-content: center;
    padding: 16px;
  }
  
  .nav-item {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .app {
    flex-direction: column;
  }
  
  .app-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  
  .sidebar-nav {
    flex-direction: row;
    padding: 8px 16px;
    overflow-x: auto;
  }
  
  .nav-item {
    padding: 8px 12px;
  }
  
  .nav-label {
    display: none;
  }
}
</style>
