<script setup>
defineProps({
  view: {
    type: String,
    required: true,
  },
});

defineEmits(['change-view']);

const navItems = [
  { key: 'dashboard', icon: '📊', label: 'Dashboard' },
  { key: 'schedule', icon: '📅', label: 'Agendar' },
  { key: 'appointments', icon: '📋', label: 'Consultas' },
  { key: 'whatsapp', icon: '💬', label: 'WhatsApp' },
];
</script>

<template>
  <header class="header">
    <div class="logo">
      <div class="logo-icon">✚</div>
      MedCare
    </div>

    <nav class="nav">
      <button
        v-for="item in navItems"
        :key="item.key"
        class="nav-btn"
        :class="{ active: view === item.key }"
        @click="$emit('change-view', item.key)"
      >
        <span>{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </nav>

    <button class="wa-badge" @click="$emit('change-view', 'whatsapp')">💬 Flow WhatsApp</button>
  </header>
</template>
