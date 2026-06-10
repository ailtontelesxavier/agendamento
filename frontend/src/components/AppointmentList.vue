<script setup>
defineProps({
  appointments: {
    type: Array,
    required: true,
  },
  statusLabel: {
    type: Function,
    required: true,
  },
  compactDate: {
    type: Boolean,
    default: false,
  },
  showActions: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['update-status']);
</script>

<template>
  <div class="appt-list">
    <div v-for="appointment in appointments" :key="appointment.id" class="appt-item">
      <div class="appt-time-col">
        <div class="appt-time">{{ appointment.time }}</div>
        <div class="appt-date-label">
          <template v-if="compactDate">{{ appointment.date.slice(8) }}/{{ appointment.date.slice(5, 7) }}</template>
          <template v-else>{{ appointment.source === 'whatsapp' ? '💬' : '🌐' }}</template>
        </div>
      </div>

      <div class="appt-info">
        <div class="appt-name">
          {{ appointment.patient_name }}
          <span v-if="appointment.source === 'whatsapp' && compactDate" class="badge badge-wa badge-inline">💬 WA</span>
        </div>
        <div class="appt-meta">{{ appointment.specialty }} · {{ appointment.doctor }}</div>
        <div v-if="compactDate" class="appt-meta">📞 {{ appointment.phone }}</div>
      </div>

      <div v-if="showActions" class="appt-actions appt-actions-column">
        <span class="badge" :class="`badge-${appointment.status}`">{{ statusLabel(appointment.status) }}</span>
        <div class="button-row">
          <button
            v-if="appointment.status === 'confirmed'"
            class="btn btn-green btn-sm"
            @click="$emit('update-status', appointment.id, 'completed')"
          >
            ✓
          </button>
          <button
            v-if="appointment.status !== 'cancelled'"
            class="btn btn-danger btn-sm"
            @click="$emit('update-status', appointment.id, 'cancelled')"
          >
            ✕
          </button>
        </div>
      </div>

      <span v-else class="badge" :class="`badge-${appointment.status}`">{{ statusLabel(appointment.status) }}</span>
    </div>
  </div>
</template>
