<script setup>
import AppointmentList from './AppointmentList.vue';
import CalendarPanel from './CalendarPanel.vue';

defineProps({
  appointmentsForDate: {
    type: Array,
    required: true,
  },
  calDays: {
    type: Array,
    required: true,
  },
  calMonthLabel: {
    type: String,
    required: true,
  },
  formatDateDisplay: {
    type: Function,
    required: true,
  },
  selectedCalDate: {
    type: String,
    required: true,
  },
  stats: {
    type: Object,
    required: true,
  },
  statsToday: {
    type: Number,
    required: true,
  },
  statusLabel: {
    type: Function,
    required: true,
  },
});

defineEmits(['next-month', 'prev-month', 'select-date']);
</script>

<template>
  <section class="view">
    <h2 class="page-title">Visão geral</h2>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total hoje</div>
        <div class="stat-val text-primary">{{ statsToday }}</div>
        <div class="stat-sub">consultas</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Confirmados</div>
        <div class="stat-val text-green">{{ stats.confirmed }}</div>
        <div class="stat-sub">agendamentos</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Via WhatsApp</div>
        <div class="stat-val text-whatsapp">{{ stats.via_whatsapp }}</div>
        <div class="stat-sub">agendamentos</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Cancelados</div>
        <div class="stat-val text-red">{{ stats.cancelled }}</div>
        <div class="stat-sub">no total</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Via Web</div>
        <div class="stat-val">{{ stats.via_web }}</div>
        <div class="stat-sub">agendamentos</div>
      </div>
    </div>

    <div class="page-grid">
      <div class="card">
        <div class="card-title">📅 Calendário</div>
        <CalendarPanel
          :cal-days="calDays"
          :month-label="calMonthLabel"
          :selected-date="selectedCalDate"
          show-appointment-dot
          @next-month="$emit('next-month')"
          @prev-month="$emit('prev-month')"
          @select-date="$emit('select-date', $event)"
        />
      </div>

      <div class="card">
        <div class="card-title">
          🗓️ Consultas - {{ formatDateDisplay(selectedCalDate) }}
          <span class="badge badge-confirmed ml-auto">{{ appointmentsForDate.length }}</span>
        </div>

        <div v-if="appointmentsForDate.length === 0" class="empty">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">Nenhuma consulta</div>
          <p class="text-sm">Clique em uma data com ponto azul para ver consultas.</p>
        </div>

        <AppointmentList v-else :appointments="appointmentsForDate" :status-label="statusLabel" />
      </div>
    </div>
  </section>
</template>
