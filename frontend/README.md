# MedCare Agendamento - Frontend

Frontend do sistema de agendamento MedCare, criado com Vue 3, Vite e pnpm.

## Requisitos

- Node.js 18+
- pnpm 9+
- Backend rodando em `http://localhost:8000`

## Instalação

```bash
pnpm install
```

## Desenvolvimento

```bash
pnpm dev
```

Por padrão, o Vite abre a aplicação em:

```text
http://localhost:5173/
```

## Build de produção

```bash
pnpm build
```

Os arquivos finais são gerados em `dist/`.

## Preview do build

```bash
pnpm preview
```

## Variáveis de ambiente

A URL da API pode ser configurada com:

```env
VITE_API_URL=http://localhost:8000
```

Se a variável não for definida, o frontend usa `http://localhost:8000`.

## Estrutura

```text
src/
  components/        Componentes Vue da interface
  composables/       Estado e regras de negócio da aplicação
  styles/            CSS global
  utils/             Funções utilitárias
  App.vue            Composição das telas principais
  constants.js       Constantes compartilhadas
  main.js            Entrada da aplicação
```

## Telas principais

- Dashboard com estatísticas e calendário.
- Fluxo de criação de consulta.
- Lista de consultas com filtros e atualização de status.
- Simulador de atendimento via WhatsApp.

## Scripts

- `pnpm dev`: inicia o servidor de desenvolvimento.
- `pnpm build`: gera o build de produção.
- `pnpm preview`: serve localmente o build gerado.
