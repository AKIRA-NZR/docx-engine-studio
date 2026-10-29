"""
Manipulador avançado de parágrafos, textos e placeholders em documentos DOCX.
Oferece suporte a substituição de tags, preenchimento de perguntas/prompts e caixas de seleção.
"""

import re
from .xml_utils import delete_paragraph_element


class ParagraphHandler:
    def __init__(self, doc):
        self.doc = doc

    @property
    def paragraphs(self):
        return self.doc.paragraphs

    def find_paragraph(self, query):
        """Retorna o primeiro parágrafo contendo o texto consultado."""
        query_clean = query.lower()
        for p in self.paragraphs:
            if query_clean in p.text.lower():
                return p
        return None

    def find_paragraph_index(self, query):
        """Retorna o índice numérico do primeiro parágrafo correspondente."""
        query_clean = query.lower()
        for idx, p in enumerate(self.paragraphs):
            if query_clean in p.text.lower():
                return idx
        return -1

    def replace_exact_text(self, old_text, new_text):
        """
        Substitui ocorrências de um texto em todos os parágrafos do documento.
        """
        count = 0
        for p in self.paragraphs:
            if old_text in p.text:
                p.text = p.text.replace(old_text, new_text)
                count += 1
        return count

    def replace_variables(self, var_map, prefix="{{", suffix="}}"):
        """
        Substitui variáveis de template no formato {{variavel}} ou customizado.
        """
        total = 0
        for key, val in var_map.items():
            placeholder = f"{prefix}{key}{suffix}"
            total += self.replace_exact_text(placeholder, str(val))
        return total

    def answer_prompt(self, prompt_query, answer_text, remove_lines_after=0):
        """
        Localiza o enunciado de uma pergunta/prompt, preenche o parágrafo de resposta
        logo abaixo dele e deleta fisicamente as linhas em branco/underscores residuais.
        """
        idx = self.find_paragraph_index(prompt_query)
        if idx == -1:
            raise ValueError(f"Prompt não localizado no documento: '{prompt_query}'")

        if idx + 1 >= len(self.paragraphs):
            raise IndexError("Não há parágrafo posterior ao prompt para inserir a resposta.")

        # Preenche o parágrafo imediatamente seguinte com a resposta
        self.paragraphs[idx + 1].text = answer_text

        # Remove fisicamente as linhas extras de travessões/sublinhados
        # Deleta de trás para frente para não alterar os índices durante a deleção
        for offset in range(remove_lines_after, 0, -1):
            target_idx = idx + 1 + offset
            if target_idx < len(self.paragraphs):
                delete_paragraph_element(self.paragraphs[target_idx])

    def select_checkbox_option(self, container_query, option_to_check):
        """
        Marca caixas de seleção do tipo '(   ) Opção' para '( X ) Opção'.
        Exemplo: select_checkbox_option('Não iniciado', 'Em testes')
        """
        p = self.find_paragraph(container_query)
        if not p:
            raise ValueError(f"Parágrafo com opções de checkbox não encontrado: '{container_query}'")

        text = p.text
        # Padrão para capturar opções como (   ) Texto
        pattern = rf"\(\s*\)\s*({re.escape(option_to_check)})"
        replacement = r"( X ) \1"

        new_text, subs = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
        if subs > 0:
            p.text = new_text
            return True
        return False
