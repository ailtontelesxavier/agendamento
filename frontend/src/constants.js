export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8022';

export const DEFAULT_APPOINTMENT_FORM = {
  specialty: '',
  doctor: '',
  date: '',
  time: '',
  patient_name: '',
  phone: '',
  notes: '',
};

export const APPOINTMENT_SLOTS = [
  '08:00',
  '08:30',
  '09:00',
  '09:30',
  '10:00',
  '10:30',
  '11:00',
  '11:30',
  '14:00',
  '14:30',
  '15:00',
  '15:30',
  '16:00',
  '16:30',
  '17:00',
];

export const WEEK_DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

export const QUICK_REPLIES = ['oi', '1', '2', '3', 'SIM', 'NÃO'];

export const WHATSAPP_FLOW_STEPS = [
  { key: 'start', icon: '👋', label: 'Saudação', desc: 'Usuário envia qualquer mensagem e recebe o menu principal.' },
  { key: 'spec', icon: '🏥', label: 'Especialidade', desc: 'Bot lista as especialidades disponíveis numeradas.' },
  { key: 'doc', icon: '👨‍⚕️', label: 'Médico', desc: 'Bot exibe os médicos da especialidade escolhida.' },
  { key: 'date', icon: '📅', label: 'Data', desc: 'Usuário informa a data no formato DD/MM/AAAA.' },
  { key: 'time', icon: '🕐', label: 'Horário', desc: 'Bot mostra horários livres; usuário escolhe no formato HH:MM.' },
  { key: 'name', icon: '👤', label: 'Nome', desc: 'Bot solicita o nome completo do paciente.' },
  { key: 'confirm', icon: '✅', label: 'Confirmação', desc: 'Bot resume o agendamento e aguarda SIM ou NÃO.' },
  { key: 'done', icon: '🎉', label: 'Concluído', desc: 'Consulta registrada e código enviado ao paciente.' },
];

export const WELCOME_MESSAGE = '👋 Olá! Bem-vindo à *Clínica MedCare*.\n\nPara agendar sua consulta, responda com o número da opção desejada:\n\n1️⃣ Agendar consulta\n2️⃣ Ver meus agendamentos\n3️⃣ Cancelar consulta\n4️⃣ Falar com atendente\n\n_Digite o número da opção:_';
