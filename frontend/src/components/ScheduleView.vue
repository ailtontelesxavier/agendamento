<script setup>
import CalendarPanel from './CalendarPanel.vue';

defineProps({
  allSlots: {
    type: Array,
    required: true,
  },
  bookedSlots: {
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
  form: {
    type: Object,
    required: true,
  },
  lastApptCode: {
    type: String,
    required: true,
  },
  schedAlert: {
    type: Object,
    default: null,
  },
  schedStep: {
    type: Number,
    required: true,
  },
  specialties: {
    type: Object,
    required: true,
  },
  submitting: {
    type: Boolean,
    required: true,
  },
});

defineEmits([
  'change-view',
  'go-step',
  'load-slots',
  'new-appointment',
  'next-month',
  'prev-month',
  'reset-doctor',
  'select-date',
  'submit',
]);
</script>

<template>
  <section class="view">
    <h2 class="page-title">Nova consulta</h2>

    <div class="steps">
      <div class="step" :class="{ done: schedStep > 1, active: schedStep === 1 }">
        <div class="step-dot">1</div>
        <div class="step-label">Especialidade</div>
      </div>
      <div class="step" :class="{ done: schedStep > 2, active: schedStep === 2 }">
        <div class="step-dot">2</div>
        <div class="step-label">Data e hora</div>
      </div>
      <div class="step" :class="{ done: schedStep > 3, active: schedStep === 3 }">
        <div class="step-dot">3</div>
        <div class="step-label">Paciente</div>
      </div>
      <div class="step" :class="{ done: schedStep > 4, active: schedStep === 4 }">
        <div class="step-dot">4</div>
        <div class="step-label">Confirmação</div>
      </div>
    </div>

    <div v-if="schedAlert" :class="`alert alert-${schedAlert.type}`">{{ schedAlert.msg }}</div>

    <div v-if="schedStep === 1" class="card">
      <div class="card-title">🏥 Escolha a especialidade</div>
      <div class="form-grid">
        <div class="form-group">
          <label>Especialidade</label>
          <select v-model="form.specialty" @change="$emit('reset-doctor')">
            <option value="">Selecione...</option>
            <option v-for="specialty in Object.keys(specialties)" :key="specialty" :value="specialty">
              {{ specialty }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Médico</label>
          <select v-model="form.doctor" :disabled="!form.specialty">
            <option value="">Selecione...</option>
            <option v-for="doctor in specialties[form.specialty] || []" :key="doctor" :value="doctor">
              {{ doctor }}
            </option>
          </select>
        </div>
      </div>
      <div class="actions-right">
        <button class="btn btn-primary" :disabled="!form.specialty || !form.doctor" @click="$emit('go-step', 2); $emit('load-slots')">
          Próximo →
        </button>
      </div>
    </div>

    <div v-if="schedStep === 2" class="page-grid">
      <div class="card">
        <div class="card-title">📅 Selecione a data</div>
        <CalendarPanel
          :cal-days="calDays"
          :month-label="calMonthLabel"
          :selected-date="form.date"
          @next-month="$emit('next-month')"
          @prev-month="$emit('prev-month')"
          @select-date="$emit('select-date', $event)"
        />
      </div>

      <div class="card">
        <div class="card-title">🕐 Horários disponíveis</div>
        <div v-if="!form.date" class="empty">
          <div class="empty-icon">📅</div>
          <p class="text-sm">Selecione uma data no calendário</p>
        </div>
        <div v-else>
          <div class="text-sm space-bottom">{{ form.doctor }} · {{ formatDateDisplay(form.date) }}</div>
          <div class="slots-grid">
            <button
              v-for="slot in allSlots"
              :key="slot"
              class="slot"
              :class="{ selected: form.time === slot, booked: bookedSlots.includes(slot) }"
              type="button"
              @click="!bookedSlots.includes(slot) && (form.time = slot)"
            >
              {{ slot }}
            </button>
          </div>
        </div>
        <div class="actions-right">
          <button class="btn btn-secondary" @click="$emit('go-step', 1)">← Voltar</button>
          <button class="btn btn-primary" :disabled="!form.date || !form.time" @click="$emit('go-step', 3)">Próximo →</button>
        </div>
      </div>
    </div>

    <div v-if="schedStep === 3" class="card">
      <div class="card-title">👤 Dados do paciente</div>
      <div class="form-grid">
        <div class="form-group">
          <label>Nome completo *</label>
          <input v-model="form.patient_name" placeholder="Nome do paciente" />
        </div>
        <div class="form-group">
          <label>Telefone / WhatsApp *</label>
          <input v-model="form.phone" placeholder="+55 63 9 9999-9999" />
        </div>
        <div class="form-group full">
          <label>Observações</label>
          <textarea v-model="form.notes" placeholder="Sintomas, histórico relevante..."></textarea>
        </div>
      </div>
      <div class="actions-right">
        <button class="btn btn-secondary" @click="$emit('go-step', 2)">← Voltar</button>
        <button class="btn btn-primary" :disabled="!form.patient_name || !form.phone" @click="$emit('go-step', 4)">Revisar →</button>
      </div>
    </div>

    <div v-if="schedStep === 4" class="card">
      <div class="card-title">✅ Confirmar agendamento</div>
      <div class="summary-grid">
        <div class="stat-card"><div class="stat-label">Especialidade</div><div class="summary-value">{{ form.specialty }}</div></div>
        <div class="stat-card"><div class="stat-label">Médico</div><div class="summary-value">{{ form.doctor }}</div></div>
        <div class="stat-card"><div class="stat-label">Data</div><div class="summary-value">{{ formatDateDisplay(form.date) }}</div></div>
        <div class="stat-card"><div class="stat-label">Horário</div><div class="summary-time">{{ form.time }}</div></div>
        <div class="stat-card"><div class="stat-label">Paciente</div><div class="summary-value">{{ form.patient_name }}</div></div>
        <div class="stat-card"><div class="stat-label">Telefone</div><div class="summary-value">{{ form.phone }}</div></div>
      </div>
      <div v-if="form.notes" class="notes-box">📝 {{ form.notes }}</div>
      <div class="actions-right">
        <button class="btn btn-secondary" @click="$emit('go-step', 3)">← Voltar</button>
        <button class="btn btn-primary" :disabled="submitting" @click="$emit('submit')">
          {{ submitting ? 'Agendando...' : '✅ Confirmar agendamento' }}
        </button>
      </div>
    </div>

    <div v-if="schedStep === 5" class="card success-card">
      <div class="success-icon">🎉</div>
      <h3>Consulta agendada!</h3>
      <p>Código: <strong>{{ lastApptCode }}</strong></p>
      <div class="actions-center">
        <button class="btn btn-primary" @click="$emit('new-appointment')">➕ Novo agendamento</button>
        <button class="btn btn-secondary" @click="$emit('change-view', 'appointments')">📋 Ver consultas</button>
      </div>
    </div>
  </section>
</template>
