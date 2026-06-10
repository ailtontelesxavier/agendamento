<script setup>
import { ref } from 'vue';

const props = defineProps({
  loading: Boolean,
  error: String,
});

const emit = defineEmits(['login']);

const cpf = ref('');
const password = ref('');

function handleSubmit() {
  const digits = cpf.value.replace(/\D/g, '');
  if (digits.length !== 11) return;
  emit('login', digits, password.value);
}

function formatCpf(value) {
  const digits = value.replace(/\D/g, '').slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function onInput(event) {
  cpf.value = formatCpf(event.target.value);
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="logo-icon">M</div>
        <span>MedCare</span>
      </div>

      <h2 class="login-title">Acesse sua conta</h2>
      <p class="login-subtitle">Entre com seu CPF e senha</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="cpf">CPF</label>
          <input
            id="cpf"
            type="text"
            inputmode="numeric"
            placeholder="000.000.000-00"
            :value="cpf"
            :disabled="loading"
            maxlength="14"
            autocomplete="username"
            @input="onInput"
          />
        </div>

        <div class="form-group">
          <label for="password">Senha</label>
          <input
            id="password"
            type="password"
            placeholder="Sua senha"
            v-model="password"
            :disabled="loading"
            autocomplete="current-password"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-block"
          :disabled="loading || cpf.replace(/\D/g, '').length !== 11 || !password"
        >
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>
