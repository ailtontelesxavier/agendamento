import { computed, ref } from 'vue';
import { API_BASE_URL } from '../constants';

const TOKEN_KEY = 'medcare_token';
const USER_KEY = 'medcare_user';

const token = ref(localStorage.getItem(TOKEN_KEY) || '');
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'));
const loginError = ref('');
const loginLoading = ref(false);

const isAuthenticated = computed(() => !!token.value);

function setAuth(tokenValue, userValue) {
  token.value = tokenValue;
  user.value = userValue;
  localStorage.setItem(TOKEN_KEY, tokenValue);
  localStorage.setItem(USER_KEY, JSON.stringify(userValue));
}

function clearAuth() {
  token.value = '';
  user.value = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function login(cpf, password) {
  loginLoading.value = true;
  loginError.value = '';

  try {
    const response = await fetch(`${API_BASE_URL}/auth/cpf-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cpf, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      loginError.value = data.detail || 'CPF ou senha inválidos';
      return false;
    }

    setAuth(data.access_token, { cpf });
    return true;
  } catch {
    loginError.value = 'Erro de conexão com o servidor';
    return false;
  } finally {
    loginLoading.value = false;
  }
}

function logout() {
  clearAuth();
}

async function authFetch(url, options = {}) {
  const headers = { ...options.headers };

  if (token.value) {
    headers['Authorization'] = `Bearer ${token.value}`;
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    clearAuth();
    throw new Error('Sessão expirada');
  }

  return response;
}

export function useAuth() {
  return {
    token,
    user,
    isAuthenticated,
    loginError,
    loginLoading,
    login,
    logout,
    authFetch,
  };
}
