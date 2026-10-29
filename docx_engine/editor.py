"""
Classe central DocumentEditor: fachada fluente e de alto nível
para automação, transformação e preenchimento de documentos Word/LibreOffice.
"""

import os
from pathlib import Path
import docx

from .table_handler import TableHandler
from .paragraph_handler import ParagraphHandler


class DocumentEditor:
    """
    Controlador central de documentos DOCX.
    Permite manipular qualquer documento de forma imperativa ou declarativa (via receitas).
    """

    def __init__(self, template_path):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Arquivo de modelo não encontrado: {self.template_path}")

        self.doc = docx.Document(str(self.template_path))
        self.tables = TableHandler(self.doc)
        self.paragraphs = ParagraphHandler(self.doc)

    # -------------------------------------------------------------------------
    # Métodos de Conveniência (Atalhos Fluentes)
    # -------------------------------------------------------------------------

    def replace_text(self, old_text, new_text):
        """Substitui ocorrências de texto simples em todo o documento."""
        self.paragraphs.replace_exact_text(old_text, new_text)
        return self

    def replace_variables(self, var_map, prefix="{{", suffix="}}"):
        """Substitui variáveis de template {{nome}}."""
        self.paragraphs.replace_variables(var_map, prefix, suffix)
        return self

    def answer_prompt(self, prompt_query, answer_text, remove_lines_after=0):
        """Preenche a resposta de um prompt e limpa as linhas vazias subsequentes."""
        self.paragraphs.answer_prompt(prompt_query, answer_text, remove_lines_after)
        return self

    def check_option(self, container_query, option_to_check):
        """Marca uma opção de checkbox, ex: '( X ) Em testes'."""
        self.paragraphs.select_checkbox_option(container_query, option_to_check)
        return self

    def fill_key_value_table(self, table_id, data_map_or_list, key_col=0, val_col=1):
        """Preenche uma tabela de dados chave-valor por nome ou lista."""
        self.tables.fill_key_value(table_id, data_map_or_list, key_col, val_col)
        return self

    def populate_grid_table(self, table_id, rows_data, ref_row_idx=1, start_row_idx=1):
        """Preenche uma tabela de grade mantendo bordas e propriedades das células."""
        self.tables.populate_grid(table_id, rows_data, ref_row_idx, start_row_idx)
        return self

    def format_tables(self, font_name="Calibri", data_size_pt=9.5, header_size_pt=10.5,
                      space_before_pt=2, space_after_pt=2, line_spacing=1.15,
                      skip_table_indices=None):
        """Padroniza a tipografia de todas as tabelas."""
        self.tables.format_typography(
            font_name=font_name,
            data_size_pt=data_size_pt,
            header_size_pt=header_size_pt,
            space_before_pt=space_before_pt,
            space_after_pt=space_after_pt,
            line_spacing=line_spacing,
            skip_table_indices=skip_table_indices
        )
        return self

    # -------------------------------------------------------------------------
    # Motor Declarativo de Receitas (Configuração via Dicionário/JSON)
    # -------------------------------------------------------------------------

    def apply_recipe(self, recipe):
        """
        Executa um conjunto estruturado de transformações definidas em um dicionário.
        Torna o preenchimento de qualquer modelo 100% orientado a configuração.
        """
        # 1. Variáveis de Template
        if "variables" in recipe:
            self.replace_variables(recipe["variables"])

        # 2. Substituições de texto direto
        for item in recipe.get("text_replacements", []):
            self.replace_text(item["find"], item["replace"])

        # 3. Checkboxes
        for item in recipe.get("checkboxes", []):
            self.check_option(item["container"], item["select"])

        # 4. Respostas de Prompts
        for item in recipe.get("prompts", []):
            self.answer_prompt(
                prompt_query=item["query"],
                answer_text=item["answer"],
                remove_lines_after=item.get("remove_lines_after", 0)
            )

        # 5. Tabelas Chave-Valor
        for item in recipe.get("key_value_tables", []):
            self.fill_key_value_table(
                table_id=item["table"],
                data_map_or_list=item["data"],
                key_col=item.get("key_col", 0),
                val_col=item.get("val_col", 1)
            )

        # 6. Tabelas Matriciais / Grid
        for item in recipe.get("grid_tables", []):
            self.populate_grid_table(
                table_id=item["table"],
                rows_data=item["data"],
                ref_row_idx=item.get("ref_row_idx", 1),
                start_row_idx=item.get("start_row_idx", 1)
            )

        # 7. Formatação de Tabelas
        if "typography" in recipe:
            typo = recipe["typography"]
            self.format_tables(**typo)

        return self

    # -------------------------------------------------------------------------
    # Inspeção de Modelos Desconhecidos
    # -------------------------------------------------------------------------

    def inspect(self):
        """
        Analisa e exibe a estrutura interna de qualquer documento desconhecido:
        tabelas, colunas, primeiros parágrafos e placeholders detectados.
        """
        print(f"\n===== Estrutura do Documento: {self.template_path.name} =====")
        print(f"Total de parágrafos: {len(self.doc.paragraphs)}")
        print(f"Total de tabelas: {len(self.doc.tables)}")

        print("\n--- Tabelas Encontradas ---")
        for idx, table in enumerate(self.doc.tables):
            header = []
            if table.rows:
                header = [c.text.strip().replace("\n", " ") for c in table.rows[0].cells[:4]]
            print(f"Tabela #{idx}: {len(table.rows)} linhas, {len(table.columns)} colunas. Início: {header}")

        return self

    # -------------------------------------------------------------------------
    # Salvamento com Tratamento de Arquivo Aberto (File Lock)
    # -------------------------------------------------------------------------

    def save(self, output_path):
        """
        Salva o documento modificado. Se o arquivo estiver aberto no Word/LibreOffice,
        grava em um caminho alternativo com sufixo '_novo.docx' sem travar o script.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.doc.save(str(out_p))
            print(f"[OK] Documento salvo com sucesso em: {out_p}")
            return str(out_p)
        except PermissionError:
            # Arquivo aberto no LibreOffice/Word
            alt_path = out_p.with_name(f"{out_p.stem}_novo{out_p.suffix}")
            self.doc.save(str(alt_path))
            print(f"[AVISO] '{out_p.name}' esta aberto em outro programa.")
            print(f"[OK] Documento salvo alternativamente em: {alt_path}")
            return str(alt_path)

    # -------------------------------------------------------------------------
    # Auditoria e Validação
    # -------------------------------------------------------------------------

    def validate(self, check_underscores=True, check_tags=True, check_empty_cells=False,
                 ignore_table_indices=None, ignore_signatures=True):
        """
        Audita o documento em memória verificando placeholders e pendências.
        """
        from .validator import DocumentValidator
        validator = DocumentValidator(self.doc)
        return validator.validate(
            check_underscores=check_underscores,
            check_tags=check_tags,
            check_empty_cells=check_empty_cells,
            ignore_table_indices=ignore_table_indices,
            ignore_signatures=ignore_signatures
        )

    # -------------------------------------------------------------------------
    # Exportação e Carga com PDF
    # -------------------------------------------------------------------------

    def export_pdf(self, output_docx_path=None, output_pdf_path=None):
        """
        Salva o DOCX e exporta automaticamente para PDF.
        """
        from .converter import docx_to_pdf
        target_docx = output_docx_path
        if target_docx is None:
            target_docx = self.save(self.template_path.with_name(f"{self.template_path.stem}_preenchido.docx"))
        else:
            self.save(target_docx)

        pdf_path = docx_to_pdf(target_docx, output_pdf_path)
        print(f"[OK] PDF exportado com sucesso em: {pdf_path}")
        return pdf_path

    @classmethod
    def from_pdf(cls, pdf_path, temp_docx=None):
        """
        Carrega um arquivo PDF, converte-o para DOCX e retorna uma instância do DocumentEditor.
        """
        from .converter import pdf_to_docx
        docx_path = pdf_to_docx(pdf_path, temp_docx)
        return cls(docx_path)
