# DOCX Engine Studio — Automação e Conversão de Documentos

Arquitetura modular em Python para manipulação, preenchimento, auditoria e conversão de documentos Word (`.docx`) e PDF (`.pdf`), com interface gráfica desktop moderna e suporte à preservação total de bordas e formatações OOXML.

---

## 🚀 Principais Funcionalidades

1. **Interface Gráfica Desktop Moderna (`app_gui.py`)**:
   - Desenvolvida com `customtkinter` (Dark/Light mode).
   - Abas para preenchimento de relatórios, conversão bidirecional PDF $\leftrightarrow$ DOCX e inspeção de modelos.
   - Botão para abrir o documento gerado diretamente no LibreOffice ou Microsoft Word.
2. **Motor Extensível para Qualquer `.docx`**:
   - Localização semântica de tabelas por cabeçalhos (imune a mudanças de ordem).
   - Clonagem perfeita de propriedades de células XML (`tcBorders`, `tcMar`, `vAlign`).
   - Prevenção automática de travamento por arquivo aberto no LibreOffice/Word (`PermissionError`).
3. **Módulo de Auditoria e Validação (`DocumentValidator`)**:
   - Verifica se restam linhas pontilhadas não respondidas (`_____`).
   - Detecta tags pendentes (`{{tag}}`) e células vazias.
   - Ignora inteligentemente campos de assinatura e avaliação docente.
4. **Conversor e Exportador Bidirecional (`converter.py`)**:
   - **PDF $\rightarrow$ DOCX**: Converte PDFs em documentos Word editáveis usando `pdf2docx`.
   - **DOCX $\rightarrow$ PDF**: Exporta automaticamente para PDF via Word COM ou LibreOffice headless.
5. **Testes Automatizados com `pytest`**:
   - Suite completa de testes cobrindo validação, conversão, clonagem de bordas e resiliência a locks.

---

## 📁 Estrutura do Projeto

```text
trabalhos/
│
├── docx_engine/                # 🚀 Motor reutilizável
│   ├── __init__.py            # Exporta DocumentEditor, Validator e Conversores
│   ├── editor.py              # Fachada central (carga, salvamento seguro e receitas)
│   ├── table_handler.py       # Busca semântica e preenchimento com clonagem de bordas
│   ├── paragraph_handler.py   # Manipulação de textos, prompts, tags e checkboxes
│   ├── validator.py           # Auditor de pendências e placeholders
│   ├── converter.py           # Conversor bidirecional PDF <-> DOCX
│   └── xml_utils.py           # Manipulação direta de nós OOXML
│
├── configs/                   # 📋 Receitas de preenchimento (dados de negócio)
│   └── mare_alerta_sprint4.py  # Dados da Sprint 4 do Maré Alerta
│
├── tests/                     # 🧪 Testes automatizados (pytest)
│   └── test_docx_engine.py
│
├── app_gui.py                 # 🖥️ Interface Gráfica Desktop Moderna
├── main.py                    # 💻 CLI para execução e inspeção
├── arquivo.py                 # 🔄 Script de compatibilidade
├── requirements.txt           # 📦 Dependências do projeto
└── README.md                  # 📖 Este documento
```

---

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🖥️ Como Usar

### 1. Pela Interface Gráfica Desktop (Recomendado)
Para abrir o estúdio gráfico completo:
```bash
python app_gui.py
```

### 2. Pela Linha de Comando (CLI)
- **Preencher o relatório padrão (Sprint 4):**
  ```bash
  python main.py
  # ou
  python arquivo.py
  ```
- **Inspecionar qualquer modelo DOCX desconhecido:**
  ```bash
  python main.py inspect SeuModelo.docx
  ```

### 3. Programaticamente no Python
```python
from docx_engine import DocumentEditor, pdf_to_docx, docx_to_pdf

# 1. Carregar e preencher
editor = DocumentEditor("Modelo.docx")
editor.replace_text("ANTIGO", "NOVO")
editor.check_option("Opções:", "Em testes")
editor.save("Resultado.docx")

# 2. Auditar documento
report = editor.validate()
print(report.summary())

# 3. Exportar para PDF
editor.export_pdf("Resultado.docx", "Resultado.pdf")

# 4. Converter PDF para Word editável
docx_editavel = pdf_to_docx("Documento.pdf")
```

---

## 🧪 Executando os Testes Automatizados

Para rodar todos os testes com relatório detalhado:

```bash
pytest -v
```
