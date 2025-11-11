# ⚛️ Frontend - Travel Planner AI Agent

Este é o frontend do Travel Planner, uma aplicação de página única (SPA) construída com **Vite, React e TypeScript**.

Esta interface permite aos utilizadores inserir detalhes da viagem num formulário de múltiplos passos, enviar esses dados para o backend de IA e visualizar o plano de viagem gerado.

## ✨ Funcionalidades

* **Formulário Multi-Step:** Experiência de utilizador guiada para recolher detalhes da viagem.
* **Validação de Dados:** Utiliza **React Hook Form** e **Zod** para validação robusta dos campos.
* **Renderização de Markdown:** Exibe o plano de viagem formatado usando `react-markdown`.
* **Visualização em Accordion:** Analisa a resposta do markdown e divide-a em secções (Voos, Hotéis, etc.) usando o componente `Accordion` da shadcn-ui.
* **Gestão de Estado:** Gestão de estado local (React state) para o plano, estado de carregamento e dados do formulário.
* **Persistência Local:** Salva e carrega planos de viagem de/para o `localStorage`.
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
* **Comunicação API**: `fetch` (para a API FastAPI)

## ⚙️ Configuração Local

### 1. Navegue até à Pasta

```bash
cd packages/frontend
```

### 2. Instalar Dependências

```bash
npm install
# ou
pnpm install
# ou
yarn install
```

### 3. Conexão com o Backend

Esta aplicação espera que o servidor backend (FastAPI) esteja a ser executado em `http://localhost:8000`.

O URL da API está definido diretamente em `src/components/TravelForm.tsx`. Para produção, recomenda-se movê-lo para um ficheiro `.env`.

## 📜 Scripts Disponíveis

* `npm run dev`: Inicia o servidor de desenvolvimento em `http://localhost:8080`.
* `npm run build`: Compila a aplicação para produção na pasta `dist/`.
* `npm run lint`: Executa o linter (ESLint) para verificar a qualidade do código.
* `npm run preview`: Pré-visualiza a build de produção localmente.