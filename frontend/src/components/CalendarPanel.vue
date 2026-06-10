<script setup>
import { WEEK_DAYS } from '../constants';

defineProps({
  calDays: {
    type: Array,
    required: true,
  },
  monthLabel: {
    type: String,
    required: true,
  },
  selectedDate: {
    type: String,
    default: '',
  },
  showAppointmentDot: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['next-month', 'prev-month', 'select-date']);
</script>

<template>
  <div class="cal-header">
    <button class="cal-nav-btn" @click="$emit('prev-month')">‹</button>
    <span class="cal-title">{{ monthLabel }}</span>
    <button class="cal-nav-btn" @click="$emit('next-month')">›</button>
  </div>

  <div class="cal-grid">
    <div v-for="dayName in WEEK_DAYS" :key="dayName" class="cal-day-name">{{ dayName }}</div>
    <button
      v-for="day in calDays"
      :key="day.key"
      class="cal-day"
      :class="{
        today: day.isToday,
        selected: selectedDate === day.dateStr,
        'other-month': !day.currentMonth,
        'has-appt': showAppointmentDot && day.hasAppt,
      }"
      type="button"
      @click="day.currentMonth && $emit('select-date', day.dateStr)"
    >
      {{ day.day }}
      <span v-if="showAppointmentDot" class="dot"></span>
    </button>
  </div>
</template>
