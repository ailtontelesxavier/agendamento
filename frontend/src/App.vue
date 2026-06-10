<script setup>
import AppHeader from './components/AppHeader.vue';
import AppointmentsView from './components/AppointmentsView.vue';
import DashboardView from './components/DashboardView.vue';
import ScheduleView from './components/ScheduleView.vue';
import WhatsAppView from './components/WhatsAppView.vue';
import { useMedcareApp } from './composables/useMedcareApp';
import { formatDateDisplay } from './utils/date';

const app = useMedcareApp();
</script>

<template>
  <AppHeader :view="app.view.value" @change-view="app.setView" />

  <main class="main">
    <div class="content">
      <DashboardView
        v-if="app.view.value === 'dashboard'"
        :appointments-for-date="app.appointmentsForDate.value"
        :cal-days="app.calDays.value"
        :cal-month-label="app.calMonthLabel.value"
        :format-date-display="formatDateDisplay"
        :selected-cal-date="app.selectedCalDate.value"
        :stats="app.stats.value"
        :stats-today="app.statsToday.value"
        :status-label="app.statusLabel"
        @next-month="app.nextMonth"
        @prev-month="app.prevMonth"
        @select-date="app.selectCalDate"
      />

      <ScheduleView
        v-if="app.view.value === 'schedule'"
        :form="app.form.value"
        :all-slots="app.allSlots"
        :booked-slots="app.bookedSlots.value"
        :cal-days="app.calDays.value"
        :cal-month-label="app.calMonthLabel.value"
        :format-date-display="formatDateDisplay"
        :last-appt-code="app.lastApptCode.value"
        :sched-alert="app.schedAlert.value"
        :sched-step="app.schedStep.value"
        :specialties="app.specialties.value"
        :submitting="app.submitting.value"
        @change-view="app.setView"
        @go-step="app.goToScheduleStep"
        @load-slots="app.loadSlots"
        @new-appointment="app.newAppointment"
        @next-month="app.nextMonth"
        @prev-month="app.prevMonth"
        @reset-doctor="app.resetSelectedDoctor"
        @select-date="app.selectFormDate"
        @submit="app.submitAppointment"
      />

      <AppointmentsView
        v-if="app.view.value === 'appointments'"
        :filter="app.filter.value"
        :appointments="app.appointments.value"
        :status-label="app.statusLabel"
        @change-view="app.setView"
        @clear-filters="app.clearFilters"
        @load-appointments="app.loadAppointments"
        @update-status="app.updateStatus"
      />

      <WhatsAppView
        v-if="app.view.value === 'whatsapp'"
        v-model:input="app.waInput.value"
        v-model:phone="app.waPhone.value"
        :bot-typing="app.waBotTyping.value"
        :flow-steps="app.waFlowSteps"
        :messages="app.waMessages.value"
        :quick-replies="app.quickReplies"
        :sessions="app.waSessions.value"
        :wa-chat-el="app.waChatEl"
        @reset-session="app.resetWaSession"
        @send-message="app.sendWaMessage"
      />
    </div>
  </main>
</template>
