export function getTodayIsoDate() {
  return new Date().toISOString().slice(0, 10);
}

export function formatDateDisplay(date) {
  if (!date) return '';

  const [year, month, day] = date.split('-');
  return `${day}/${month}/${year}`;
}

export function formatCurrentTime() {
  return new Date().toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}
