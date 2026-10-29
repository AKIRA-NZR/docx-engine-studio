# DOCX Engine Studio — Automação e Conversão de Documentos

Motor modular em Python para automação de modificações, preenchimento, auditoria e conversão bidirecional (PDF $\leftrightarrow$ DOCX) de qualquer documento Word (`.docx`).

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

4. **Interface Gráfica Desktop Moderna (`app_gui.py`)**:
   - Interface em Dark Mode nativa construída com `customtkinter`.
   - Abas dedicadas para:
     - 📄 Preenchimento e auditoria de documentos.
     - 🔄 Conversão de PDF para DOCX e vice-versa.
     - 🔍 Inspeção estrutural de modelos desconhecidos.
   - Inicializador de 2 cliques para Windows (`Abrir_Studio.bat`).

---

## 📁 Estrutura do Projeto

```text
trabalhos/
│
├── docx_engine/                # 🚀 Motor reutilizável para qualquer documento
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
├── app_gui.py                 # 🖥️ Interface Gráfica Desktop Moderna
├── Abrir_Studio.bat           # ⚡ Atalho de inicialização rápida no Windows
├── main.py                    # 💻 CLI para execução e inspeção
├── arquivo.py                 # 🔄 Script de compatibilidade
├── requirements.txt           # 📦 Dependências do projeto
└── README.md                  # 📖 Este documento
```

---

## 📦 Instalação

```bash
pip install -r requirements.txt
```

---

## 🖥️ Como Usar

### 1. Pela Interface Gráfica Desktop (Recomendado)
Execute no terminal:
```bash
python app_gui.py
```
*Ou dê dois cliques no arquivo `Abrir_Studio.bat` no Windows Explorer.*

### 2. Pela Linha de Comando (CLI)
- **Preencher o relatório padrão de exemplo:**
  ```bash
  python main.py
  ```
- **Inspecionar qualquer modelo DOCX desconhecido:**
  ```bash
  python main.py inspect SeuModelo.docx
  ```

### 3. Programaticamente no Python
```python
from docx_engine import DocumentEditor, pdf_to_docx, docx_to_pdf

# 1. Carregar e preencher qualquer modelo
editor = DocumentEditor("MeuModelo.docx")
editor.replace_text("TEXTO_ANTIGO", "TEXTO_NOVO")
editor.check_option("Opções:", "Concluído")
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

```bash
pytest -v
```
