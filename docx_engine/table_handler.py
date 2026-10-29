"""
Gerenciador e manipulador avançado de tabelas DOCX.
Oferece busca semântica de tabelas, preenchimento dinâmico e clonagem de estilos.
"""

from docx.shared import Pt
from .xml_utils import clone_cell_properties, get_cell_text_clean


class TableHandler:
    def __init__(self, doc):
        self.doc = doc

    @property
    def tables(self):
        return self.doc.tables

    def get_table(self, identifier):
        """
        Retorna uma tabela pelo índice inteiro ou por busca semântica (cabeçalhos / textos).
        """
        if isinstance(identifier, int):
            if 0 <= identifier < len(self.tables):
                return self.tables[identifier]
            raise IndexError(f"Tabela no índice {identifier} não existe no documento (total: {len(self.tables)}).")

        if isinstance(identifier, (list, tuple, set)):
            return self.find_table_by_headers(identifier)

        if isinstance(identifier, str):
            return self.find_table_by_text(identifier)

        raise ValueError(f"Identificador de tabela inválido: {identifier}")

    def find_table_by_headers(self, expected_headers, min_matches=1):
        """
        Localiza a tabela cujo cabeçalho (linha 0) contenha as colunas esperadas.
        Torna a automação imune a alterações de ordem de tabelas no documento.
        """
        expected_lower = [h.lower() for h in expected_headers]
        best_table = None
        max_matched = 0

        for table in self.tables:
            if not table.rows:
                continue
            header_row = [get_cell_text_clean(c).lower() for c in table.rows[0].cells]
            matches = sum(1 for exp in expected_lower if any(exp in h for h in header_row))
            if matches >= min_matches and matches > max_matched:
                max_matched = matches
                best_table = table

        if best_table:
            return best_table
        raise ValueError(f"Nenhuma tabela encontrada com os cabeçalhos: {expected_headers}")

    def find_table_by_text(self, text):
        """Localiza a primeira tabela que contém determinado texto em qualquer célula."""
        text_lower = text.lower()
        for table in self.tables:
            for row in table.rows:
                for cell in row.cells:
                    if text_lower in cell.text.lower():
                        return table
        raise ValueError(f"Nenhuma tabela encontrada contendo o texto: '{text}'")

    def fill_key_value(self, table_id, data_map_or_list, key_col=0, val_col=1):
        """
        Preenche tabelas de chave-valor (ex: Tabela de Identificação e Configuração).
        Se data_map_or_list for dict: busca a chave na coluna `key_col` e preenche `val_col`.
        Se for list: preenche ordenadamente a coluna `val_col` a partir da linha 0 ou 1.
        """
        table = self.get_table(table_id)

        if isinstance(data_map_or_list, dict):
            for target_key, value in data_map_or_list.items():
                target_clean = target_key.lower().strip()
                matched = False
                for row in table.rows:
                    cell_text = row.cells[key_col].text.lower().strip()
                    if target_clean in cell_text or cell_text in target_clean:
                        row.cells[val_col].text = str(value)
                        matched = True
                        break
                if not matched:
                    # Se não encontrou linha com o rótulo, pode registrar ou ignorar
                    pass

        elif isinstance(data_map_or_list, (list, tuple)):
            for idx, value in enumerate(data_map_or_list):
                if idx < len(table.rows):
                    table.rows[idx].cells[val_col].text = str(value)

        return table

    def populate_grid(self, table_id, rows_data, ref_row_idx=1, start_row_idx=1):
        """
        Popula tabelas matriciais (ex: Endpoints, Histórico, Funcionalidades, Telas).
        - Clona automaticamente propriedades OOXML da linha de referência para novas linhas.
        - Preenche os dados por coluna.
        """
        table = self.get_table(table_id)
        if not table.rows:
            return table

        # Garante a linha de referência para cópia de bordas/margens
        ref_row = table.rows[ref_row_idx] if len(table.rows) > ref_row_idx else table.rows[0]

        # Expande a tabela caso hajam mais dados do que linhas disponíveis
        needed_rows = start_row_idx + len(rows_data)
        while len(table.rows) < needed_rows:
            new_row = table.add_row()
            for c_idx, cell in enumerate(new_row.cells):
                if c_idx < len(ref_row.cells):
                    clone_cell_properties(ref_row.cells[c_idx], cell)

        # Preenche os valores
        for r_offset, row_values in enumerate(rows_data):
            target_row = table.rows[start_row_idx + r_offset]
            if isinstance(row_values, (list, tuple)):
                for c_idx, val in enumerate(row_values):
                    if c_idx < len(target_row.cells):
                        target_row.cells[c_idx].text = str(val) if val is not None else ""
            elif isinstance(row_values, dict):
                # Se for dict, preenche conforme o índice ou nome da coluna se houver mapeamento
                for c_idx, (k, val) in enumerate(row_values.items()):
                    if c_idx < len(target_row.cells):
                        target_row.cells[c_idx].text = str(val) if val is not None else ""

        return table

    def format_typography(self, font_name="Calibri", data_size_pt=9.5, header_size_pt=10.5,
                          space_before_pt=2, space_after_pt=2, line_spacing=1.15,
                          skip_table_indices=None):
        """
        Aplica formatação tipográfica consistente em todas as tabelas do documento.
        """
        skip_indices = skip_table_indices or []
        for t_idx, table in enumerate(self.tables):
            if t_idx in skip_indices:
                continue

            for row_idx, row in enumerate(table.rows):
                # Determina se é cabeçalho (geralmente linha 0 de tabelas com mais de 1 linha)
                is_header = (row_idx == 0 and len(table.rows) > 1)

                for c_idx, cell in enumerate(row.cells):
                    for p in cell.paragraphs:
                        p.paragraph_format.space_before = Pt(space_before_pt)
                        p.paragraph_format.space_after = Pt(space_after_pt)
                        p.paragraph_format.line_spacing = line_spacing

                        for r in p.runs:
                            r.font.name = font_name
                            if not is_header:
                                r.font.size = Pt(data_size_pt)
                            elif header_size_pt is not None:
                                r.font.size = Pt(header_size_pt)
