# DOCX Engine Studio — Automação e Conversão de Documentos

Motor modular em Python com **Frontend Web em React + TypeScript** e **Interface Desktop** para automação de modificações, preenchimento, auditoria de conformidade e conversão bidirecional (PDF $\leftrightarrow$ DOCX) de qualquer documento Word (`.docx`).

---

## 🎯 Objetivo do Projeto

O objetivo principal do **DOCX Engine Studio** é receber qualquer documento e automatizar todo o processo de modificação estrutural, além de fornecer auditoria/validação de conformidade e conversão de formatos:

1. **Automação de Modificações e Preenchimento**:
   - Preenchimento inteligente de tabelas chave-valor e matriciais (grid).
   - Clonagem profunda de propriedades XML (`tcBorders`, `tcMar`, `vAlign`, `shd`) para que linhas adicionadas dinamicamente preservem 100% da identidade visual original.
   - Respostas de perguntas/prompts com remoção de parágrafos residuais vazios da árvore XML.
   - Marcação automática de caixas de seleção (`(   )` para `( X )`).
   - Imunidade a deslocamento de tabelas (busca semântica por cabeçalhos em vez de índices estáticos).

2. **Auditoria e Validação (`DocumentValidator`)**:
   - Analisa o documento em memória antes de salvar.
   - Detecta linhas de sublinhado não preenchidas (`_____`), tags de template esquecidas (`{{tag}}`) e células em branco.
   - Ignora inteligentemente campos de assinatura e seções de avaliação docente.

3. **Conversão Bidirecional (PDF $\leftrightarrow$ DOCX)**:
   - **PDF $\rightarrow$ DOCX**: Converte arquivos PDF em documentos Word totalmente editáveis via `pdf2docx`.
   - **DOCX $\rightarrow$ PDF**: Exportação direta para PDF com fallback para LibreOffice headless.

4. **Frontend Web Moderno (`frontend/` — React 19 + TypeScript + Vite)**:
   - Dashboard em Dark Mode conectado à API FastAPI (`api_server.py`).
   - Editor JSON interativo de receitas declarativas, upload de modelos `.docx`, relatórios visuais de auditoria e download instantâneo de `.docx` e `.pdf`.

5. **Interface Gráfica Desktop (`app_gui.py`)**:
   - Interface nativa construída com `customtkinter`.

---

## 📁 Estrutura do Projeto

```text
trabalhos/
│
├── frontend/                   # 🌐 Aplicação Web React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx            # Dashboard com 4 abas (Automação, Validador, Conversor, Inspetor)
│   │   ├── App.css            # Design system em Dark Mode
│   │   ├── types.ts           # Contratos TypeScript da API
│   │   └── main.tsx           # Ponto de entrada React
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts         # Proxy configurado para http://127.0.0.1:8000
│
├── docx_engine/                # 🚀 Motor Python reutilizável para qualquer documento
│   ├── __init__.py            # Exporta DocumentEditor, Validator e Conversores
│   ├── editor.py              # Fachada central (carga, salvamento seguro e receitas)
│   ├── table_handler.py       # Busca semântica e preenchimento com clonagem de bordas
│   ├── paragraph_handler.py   # Manipulação de textos, prompts, tags e checkboxes
│   ├── validator.py           # Auditor de pendências e placeholders
│   ├── converter.py           # Conversor bidirecional PDF <-> DOCX
│   └── xml_utils.py           # Manipulação direta de nós OOXML
│
├── configs/                   # 📋 Receitas de preenchimento (dados de negócio)
│   └── exemplo_relatorio.py   # Receita declarativa de exemplo
│
├── tests/                     # 🧪 Testes automatizados (pytest)
│   └── test_docx_engine.py
│
├── api_server.py              # ⚡ Servidor REST FastAPI para o Frontend React
├── Iniciar_Web.bat            # 🌐 Atalho de 2 cliques para abrir a versão Web
├── app_gui.py                 # 🖥️ Interface Gráfica Desktop Nativa
├── Abrir_Studio.bat           # ⚡ Atalho de 2 cliques para a interface Desktop
├── main.py                    # 💻 CLI para execução e inspeção
├── requirements.txt           # 📦 Dependências Python
└── README.md                  # 📖 Este documento
```

---

## 🚀 Como Executar o Frontend Web (React + FastAPI)

### Opção Rápida (1 Clique no Windows)
Dê dois cliques em **`Iniciar_Web.bat`** — ele inicia o servidor em `http://127.0.0.1:8000` e abre o navegador automaticamente.

### Opção em Modo de Desenvolvimento (Vite Hot Reload)
1. **Terminal 1 (Backend FastAPI):**
   ```bash
   python api_server.py
   ```
2. **Terminal 2 (Frontend React + TypeScript):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Acesse **`http://localhost:5173`**.

---

## 🧪 Executando os Testes Automatizados

```bash
pytest -v
```
