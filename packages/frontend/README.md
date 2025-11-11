# ⚛️ Frontend - Travel Planner AI Agent

Este é o frontend do Travel Planner, uma aplicação de página única (SPA) construída com **Vite, React e TypeScript**.

Esta interface permite aos utilizadores inserir detalhes da viagem num formulário de múltiplos passos, enviar esses dados para o backend de IA e visualizar o plano de viagem gerado via streaming.

## ✨ Funcionalidades

* **Formulário Multi-Step:** Experiência de utilizador guiada para recolher detalhes da viagem.
* **Validação de Dados:** Utiliza **React Hook Form** e **Zod** para validação robusta dos campos.
* **Renderização em Tempo Real:** Recebe a resposta do backend via `fetch` stream e atualiza a UI token por token com `ReactMarkdown`.
* **Visualização em Accordion:** Analisa a resposta do markdown e divide-a em secções (Voos, Hotéis, etc.) usando o componente `Accordion` da shadcn-ui.
* **Persistência Local:** Salva e carrega planos de viagem de/para o `localStorage` na página "Meus Planos".
* **Exportação para PDF:** Utiliza `jspdf` e `html2canvas` para permitir o download do plano de viagem.
* **Tema Light/Dark:** Suporte completo para temas usando o `ThemeProvider`.

## 🛠️ Pilha Tecnológica

* **Build Tool**: Vite
* **Framework**: React 18
* **Linguagem**: TypeScript
* **Estilização**: Tailwind CSS
* **Componentes UI**: shadcn-ui (construído sobre Radix UI)
* **Formulários**: React Hook Form & Zod
* **Routing**: React Router

## ⚙️ Configuração Local

### 1. Navegue até à Pasta

```bash
# A partir da raiz do projeto
cd packages/frontend
```

### 2. Instalar Dependências

```bash
npm install
# ou
pnpm install
# ou
bun install
```

### 3. Conexão com o Backend

Esta aplicação precisa de um ficheiro `.env` na raiz (`packages/frontend/`) para saber onde está a API.

Crie o ficheiro `packages/frontend/.env` com o seguinte conteúdo:

```env
# .env
VITE_API_URL=http://localhost:8000
```

Certifique-se de que o servidor backend está a ser executado no URL especificado (ex: `http://localhost:8000`).

## 📜 Scripts Disponíveis

* `npm run dev`: Inicia o servidor de desenvolvimento (por defeito em `http://localhost:8080`).
* `npm run build`: Compila a aplicação para produção na pasta `dist/`.
* `npm run lint`: Executa o linter (ESLint) para verificar a qualidade do código.
* `npm run preview`: Pré-visualiza a build de produção localmente.