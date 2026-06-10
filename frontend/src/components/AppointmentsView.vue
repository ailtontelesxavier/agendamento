<script setup>
import AppointmentList from './AppointmentList.vue';

defineProps({
  appointments: {
    type: Array,
    required: true,
  },
  filter: {
    type: Object,
    required: true,
  },
  statusLabel: {
    type: Function,
    required: true,
  },
});

defineEmits(['change-view', 'clear-filters', 'load-appointments', 'update-status']);
</script>

<template>
  <section class="view">
    <div class="page-toolbar">
      <h2 class="page-title no-margin">Consultas agendadas</h2>
      <div class="toolbar-actions">
        <select v-model="filter.status" class="control-sm" @change="$emit('load-appointments')">
          <option value="">Todos os status</option>
          <option value="confirmed">Confirmados</option>
          <option value="cancelled">Cancelados</option>
          <option value="completed">Concluídos</option>
        </select>
        <input v-model="filter.date" type="date" class="control-sm" @change="$emit('load-appointments')" />
        <button class="btn btn-secondary btn-sm" @click="$emit('clear-filters')">Limpar</button>
        <button class="btn btn-primary btn-sm" @click="$emit('change-view', 'schedule')">➕ Agendar</button>
      </div>
    </div>

    <div v-if="appointments.length === 0" class="empty empty-large">
      <div class="empty-icon">📭</div>
      <div class="empty-title">Nenhuma consulta encontrada</div>
      <p class="text-sm">Ajuste os filtros ou agende uma nova consulta.</p>
    </div>

    <AppointmentList
      v-else
      :appointments="appointments"
      compact-date
      show-actions
      :status-label="statusLabel"
      @update-status="(...args) => $emit('update-status', ...args)"
    />
  </section>
</template>
