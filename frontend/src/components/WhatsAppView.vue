<script setup>
defineProps({
  botTyping: {
    type: Boolean,
    required: true,
  },
  flowSteps: {
    type: Array,
    required: true,
  },
  input: {
    type: String,
    required: true,
  },
  messages: {
    type: Array,
    required: true,
  },
  phone: {
    type: String,
    required: true,
  },
  quickReplies: {
    type: Array,
    required: true,
  },
  sessions: {
    type: Array,
    required: true,
  },
  waChatEl: {
    type: Object,
    required: true,
  },
});

defineEmits(['reset-session', 'send-message', 'update:input', 'update:phone']);
</script>

<template>
  <section class="view">
    <h2 class="page-title">Flow WhatsApp</h2>

    <div class="page-grid">
      <div>
        <div class="wa-panel">
          <div class="wa-header">
            <div class="wa-avatar">💬</div>
            <div>
              <div class="wa-name">Bot MedCare</div>
              <div class="wa-status">🟢 Online</div>
            </div>
            <div class="wa-header-actions">
              <span>{{ phone }}</span>
              <button class="btn btn-sm wa-reset-btn" @click="$emit('reset-session')">↺</button>
            </div>
          </div>

          <div :ref="(el) => (waChatEl.value = el)" class="wa-chat">
            <div v-for="(message, index) in messages" :key="index" class="wa-msg" :class="message.from === 'bot' ? 'bot' : 'user-msg'">
              <span class="preserve-lines">{{ message.text }}</span>
              <div class="ts">{{ message.time }}</div>
            </div>
            <div v-if="botTyping" class="wa-msg bot">
              <span class="typing">digitando...</span>
            </div>
          </div>

          <div class="wa-input-row">
            <input
              class="wa-input"
              :value="input"
              placeholder="Digite sua mensagem..."
              @input="$emit('update:input', $event.target.value)"
              @keyup.enter="$emit('send-message')"
            />
            <button class="wa-send-btn" @click="$emit('send-message')">➤</button>
          </div>
        </div>

        <div class="quick-replies">
          <div class="text-sm space-bottom-sm">Respostas rapidas:</div>
          <div class="flex-row">
            <button
              v-for="reply in quickReplies"
              :key="reply"
              class="btn btn-secondary btn-sm"
              @click="$emit('update:input', reply); $emit('send-message')"
            >
              {{ reply }}
            </button>
          </div>
        </div>
      </div>

      <div class="col">
        <div class="card">
          <div class="card-title">🗺️ Fluxo do bot</div>
          <div class="flow-list">
            <div v-for="step in flowSteps" :key="step.key" class="flow-item">
              <span>{{ step.icon }}</span>
              <div>
                <strong>{{ step.label }}</strong>
                <div>{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">📡 Simular webhook</div>
          <p class="text-sm space-bottom">Envie mensagens diretamente para a API do backend:</p>
          <div class="form-group space-bottom-sm">
            <label>Número do paciente</label>
            <input :value="phone" placeholder="556399999999" @input="$emit('update:phone', $event.target.value)" />
          </div>
          <div class="form-group space-bottom-sm">
            <label>Mensagem</label>
            <input
              :value="input"
              placeholder="Ex: 1"
              @input="$emit('update:input', $event.target.value)"
              @keyup.enter="$emit('send-message')"
            />
          </div>
          <button class="btn btn-primary full-width" @click="$emit('send-message')">📤 Enviar para webhook</button>
        </div>

        <div class="card">
          <div class="card-title">📊 Sessões ativas</div>
          <div v-if="sessions.length === 0" class="empty empty-compact">
            <p class="text-sm">Nenhuma sessão ativa</p>
          </div>
          <div v-else class="session-list">
            <div v-for="session in sessions" :key="session.phone" class="session-item">
              <span>📱</span>
              <span class="session-phone">{{ session.phone }}</span>
              <span class="badge badge-pending ml-auto">{{ session.step }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
