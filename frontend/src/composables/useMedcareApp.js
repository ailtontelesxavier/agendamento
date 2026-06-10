/**
 * Composable principal do sistema de agendamento MedCare.
 *
 * Gerencia estado do dashboard, calendário, agendamentos, WhatsApp bot,
 * formulário de agendamento e todas as chamadas à API.
 *
 * @module useMedcareApp
 */
import { computed, nextTick, onMounted, ref } from 'vue';
import {
  API_BASE_URL,
  APPOINTMENT_SLOTS,
  DEFAULT_APPOINTMENT_FORM,
  QUICK_REPLIES,
  WELCOME_MESSAGE,
  WHATSAPP_FLOW_STEPS,
} from '../constants';
import { formatCurrentTime, getTodayIsoDate } from '../utils/date';

/** Labels amigáveis para os status de agendamento */
const STATUS_LABELS = {
  confirmed: 'Confirmado',
  cancelled: 'Cancelado',
  completed: 'Concluído',
  pending: 'Pendente',
};

/**
 * Gera os 42 dias para exibição no calendário (6 semanas).
 * @param {object} params
 * @param {number} params.year - Ano do calendário
 * @param {number} params.month - Mês (0-11)
 * @param {string} params.today - Data de hoje em ISO (YYYY-MM-DD)
 * @param {Array} params.appointments - Lista de agendamentos
 * @returns {Array<object>} Array de objetos { day, dateStr, currentMonth, isToday, hasAppt, key }
 */
  const firstDate = new Date(year, month, 1);
  const lastDate = new Date(year, month + 1, 0);
  const days = [];

  for (let index = 0; index < firstDate.getDay(); index += 1) {
    const date = new Date(year, month, -firstDate.getDay() + 1 + index);

    days.push({
      day: date.getDate(),
      dateStr: date.toISOString().slice(0, 10),
      currentMonth: false,
      isToday: false,
      hasAppt: false,
      key: `prev-${index}`,
    });
  }

  for (let day = 1; day <= lastDate.getDate(); day += 1) {
    const date = new Date(year, month, day);
    const dateStr = date.toISOString().slice(0, 10);

    days.push({
      day,
      dateStr,
      currentMonth: true,
      isToday: dateStr === today,
      hasAppt: appointments.some((appointment) => appointment.date === dateStr && appointment.status !== 'cancelled'),
      key: dateStr,
    });
  }

  const nextMonthDays = 42 - days.length;

  for (let index = 1; index <= nextMonthDays; index += 1) {
    const date = new Date(year, month + 1, index);

    days.push({
      day: date.getDate(),
      dateStr: date.toISOString().slice(0, 10),
      currentMonth: false,
      isToday: false,
      hasAppt: false,
      key: `next-${index}`,
    });
  }

  return days;
}

/** Cria uma cópia do formulário padrão de agendamento. */
function createDefaultForm() {
  return { ...DEFAULT_APPOINTMENT_FORM };
}

/**
 * Composable principal do MedCare.
 * @param {object} auth - Objeto retornado por useAuth() (precisa de authFetch)
 * @returns {object} Todo o estado e métodos reativos do aplicativo
 */
export function useMedcareApp(auth) {
  const view = ref('dashboard');
  const today = getTodayIsoDate();

  const calYear = ref(new Date().getFullYear());
  const calMonth = ref(new Date().getMonth());
  const selectedCalDate = ref(today);

  const appointments = ref([]);
  const filter = ref({ status: '', date: '' });
  const stats = ref({ confirmed: 0, cancelled: 0, completed: 0, via_whatsapp: 0, via_web: 0, total: 0 });

  const schedStep = ref(1);
  const schedAlert = ref(null);
  const submitting = ref(false);
  const lastApptCode = ref('');
  const specialties = ref({});
  const bookedSlots = ref([]);
  const form = ref(createDefaultForm());

  const waPhone = ref('556392345678');
  const waInput = ref('');
  const waMessages = ref([]);
  const waBotTyping = ref(false);
  const waSessions = ref([]);
  const waChatEl = ref(null);

  const calMonthLabel = computed(() => {
    const date = new Date(calYear.value, calMonth.value, 1);

    return date
      .toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
      .replace(/^\w/, (letter) => letter.toUpperCase());
  });

  const calDays = computed(() =>
    createCalendarDays({
      year: calYear.value,
      month: calMonth.value,
      today,
      appointments: appointments.value,
    }),
  );

  const appointmentsForDate = computed(() =>
    appointments.value
      .filter((appointment) => appointment.date === selectedCalDate.value)
      .sort((current, next) => current.time.localeCompare(next.time)),
  );

  const statsToday = computed(
    () => appointments.value.filter((appointment) => appointment.date === today && appointment.status !== 'cancelled').length,
  );

  function prevMonth() {
    if (calMonth.value === 0) {
      calMonth.value = 11;
      calYear.value -= 1;
      return;
    }

    calMonth.value -= 1;
  }

  function nextMonth() {
    if (calMonth.value === 11) {
      calMonth.value = 0;
      calYear.value += 1;
      return;
    }

    calMonth.value += 1;
  }

  function selectCalDate(date) {
    selectedCalDate.value = date;
  }

  /** Carrega estatísticas gerais do backend. */
  async function loadStats() {
    try {
      const response = await auth.authFetch(`${API_BASE_URL}/stats`);
      stats.value = await response.json();
    } catch {
      stats.value = { confirmed: 0, cancelled: 0, completed: 0, via_whatsapp: 0, via_web: 0, total: 0 };
    }
  }

  /** Carrega agendamentos com filtros aplicados (status, data). */
  async function loadAppointments() {
    try {
      const params = new URLSearchParams();

      if (filter.value.status) params.set('status', filter.value.status);
      if (filter.value.date) params.set('date', filter.value.date);

      const response = await auth.authFetch(`${API_BASE_URL}/appointments?${params}`);
      const data = await response.json();

      appointments.value = data.appointments || [];
    } catch {
      appointments.value = [];
    }
  }

  /**
   * Atualiza o status de um agendamento.
   * @param {string} id - UUID do agendamento
   * @param {string} status - Novo status (confirmed, cancelled, completed)
   */
  async function updateStatus(id, status) {
    await auth.authFetch(`${API_BASE_URL}/appointments/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });

    await Promise.all([loadAppointments(), loadStats()]);
  }

  function statusLabel(status) {
    return STATUS_LABELS[status] || status;
  }

  async function loadSpecialties() {
    try {
      const response = await fetch(`${API_BASE_URL}/specialties`);
      const data = await response.json();

      specialties.value = data.doctors || {};
    } catch {
      specialties.value = {};
    }
  }

  async function loadSlots() {
    if (!form.value.doctor || !form.value.date) return;

    try {
      const doctor = encodeURIComponent(form.value.doctor);
      const response = await auth.authFetch(`${API_BASE_URL}/available-slots?doctor=${doctor}&date=${form.value.date}`);
      const data = await response.json();

      bookedSlots.value = data.booked || [];
    } catch {
      bookedSlots.value = [];
    }
  }

  function selectFormDate(date) {
    form.value.date = date;
    form.value.time = '';
    loadSlots();
  }

  function resetSelectedDoctor() {
    form.value.doctor = '';
  }

  function goToScheduleStep(step) {
    schedStep.value = step;
  }

  /** Envia o formulário de agendamento para o backend. */
  async function submitAppointment() {
    submitting.value = true;
    schedAlert.value = null;

    try {
      const response = await auth.authFetch(`${API_BASE_URL}/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form.value),
      });

      if (!response.ok) {
        const error = await response.json();
        schedAlert.value = { type: 'error', msg: error.detail || 'Erro ao agendar' };
        schedStep.value = 2;
        return;
      }

      const data = await response.json();
      lastApptCode.value = data.appointment.id.slice(0, 8).toUpperCase();
      schedStep.value = 5;

      await Promise.all([loadAppointments(), loadStats()]);
    } catch {
      schedAlert.value = { type: 'error', msg: 'Erro de conexão com o servidor' };
    } finally {
      submitting.value = false;
    }
  }

  function newAppointment() {
    form.value = createDefaultForm();
    schedStep.value = 1;
    schedAlert.value = null;
    bookedSlots.value = [];
  }

  async function scrollChat() {
    await nextTick();

    if (waChatEl.value) {
      waChatEl.value.scrollTop = waChatEl.value.scrollHeight;
    }
  }

  /** Envia mensagem para o bot WhatsApp e exibe a resposta. */
  async function sendWaMessage() {
    const message = waInput.value.trim();

    if (!message) return;

    waMessages.value.push({ from: 'user', text: message, time: formatCurrentTime() });
    waInput.value = '';
    waBotTyping.value = true;

    await scrollChat();

    try {
      const response = await fetch(`${API_BASE_URL}/whatsapp/webhook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_number: waPhone.value, message }),
      });
      const data = await response.json();

      window.setTimeout(async () => {
        waBotTyping.value = false;
        waMessages.value.push({ from: 'bot', text: data.message, time: formatCurrentTime() });

        await scrollChat();
        await Promise.all([loadWaSessions(), loadAppointments(), loadStats()]);
      }, 600);
    } catch {
      waBotTyping.value = false;
      waMessages.value.push({ from: 'bot', text: 'Erro de conexão com o servidor.', time: formatCurrentTime() });
    }
  }

  async function resetWaSession() {
    await auth.authFetch(`${API_BASE_URL}/whatsapp/reset/${waPhone.value}`, { method: 'POST' }).catch(() => {});
    waMessages.value = [];

    await loadWaSessions();
  }

  async function loadWaSessions() {
    try {
      const response = await auth.authFetch(`${API_BASE_URL}/whatsapp/sessions`);
      const data = await response.json();

      waSessions.value = Object.values(data.sessions || {});
    } catch {
      waSessions.value = [];
    }
  }

  function setView(nextView) {
    view.value = nextView;
  }

  function clearFilters() {
    filter.value = { status: '', date: '' };
    loadAppointments();
  }

  onMounted(async () => {
    await Promise.all([loadSpecialties(), loadAppointments(), loadStats(), loadWaSessions()]);

    waMessages.value.push({
      from: 'bot',
      text: WELCOME_MESSAGE,
      time: formatCurrentTime(),
    });
  });

  return {
    view,
    setView,
    calMonthLabel,
    calDays,
    selectedCalDate,
    prevMonth,
    nextMonth,
    selectCalDate,
    appointmentsForDate,
    stats,
    statsToday,
    appointments,
    filter,
    clearFilters,
    loadAppointments,
    updateStatus,
    statusLabel,
    schedStep,
    schedAlert,
    submitting,
    lastApptCode,
    specialties,
    bookedSlots,
    allSlots: APPOINTMENT_SLOTS,
    form,
    resetSelectedDoctor,
    goToScheduleStep,
    loadSlots,
    selectFormDate,
    submitAppointment,
    newAppointment,
    waPhone,
    waInput,
    waMessages,
    waBotTyping,
    waSessions,
    waChatEl,
    quickReplies: QUICK_REPLIES,
    waFlowSteps: WHATSAPP_FLOW_STEPS,
    sendWaMessage,
    resetWaSession,
  };
}
