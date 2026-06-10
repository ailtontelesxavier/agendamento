/**
 * Composable de autenticação JWT para o MedCare.
 *
 * Fornece login por CPF + senha, logout, persistência de token no localStorage,
 * e um wrapper authFetch() que injeta o Bearer token nas requisições.
 *
 * @module useAuth
 */
import { computed, ref } from 'vue';
import { API_BASE_URL } from '../constants';

const TOKEN_KEY = 'medcare_token';
const USER_KEY = 'medcare_user';

const token = ref(localStorage.getItem(TOKEN_KEY) || '');
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'));
const loginError = ref('');
const loginLoading = ref(false);

/** @type {import('vue').ComputedRef<boolean>} True se o usuário está autenticado */
const isAuthenticated = computed(() => !!token.value);

/**
 * Salva token e dados do usuário no estado e localStorage.
 * @param {string} tokenValue - Token JWT
 * @param {object} userValue - Dados do usuário (ex: { cpf })
 */
function setAuth(tokenValue, userValue) {
  token.value = tokenValue;
  user.value = userValue;
  localStorage.setItem(TOKEN_KEY, tokenValue);
  localStorage.setItem(USER_KEY, JSON.stringify(userValue));
}

/** Limpa autenticação do estado e localStorage. */
function clearAuth() {
  token.value = '';
  user.value = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Autentica um usuário por CPF + senha.
 * @param {string} cpf - CPF do usuário (11 dígitos)
 * @param {string} password - Senha do usuário
 * @returns {Promise<boolean>} True se login foi bem-sucedido
 */
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

/** Faz logout limpando a autenticação. */
function logout() {
  clearAuth();
}

/**
 * Wrapper de fetch() que injeta o Bearer token automaticamente.
 * Se retornar 401, limpa a autenticação e lança erro.
 *
 * @param {string} url - URL da requisição
 * @param {RequestInit} options - Opções do fetch (method, headers, body, etc)
 * @returns {Promise<Response>} Resposta do fetch
 * @throws {Error} Se a sessão expirar (status 401)
 */
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

/**
 * Composable principal de autenticação.
 * @returns {object} Objeto com token, user, isAuthenticated, login, logout, authFetch
 */
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
