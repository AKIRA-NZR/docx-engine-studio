"""
Utilitários de manipulação direta de XML (Office Open XML - OOXML).
Permite manter a fidelidade visual de tabelas, bordas, margens e parágrafos.
"""

import copy
from docx.oxml.ns import qn

# Propriedades de célula essenciais para preservar bordas, espaçamento e alinhamento
CLONEABLE_CELL_PROPERTIES = [
    'tcBorders',  # Bordas individuais (topo, base, esquerda, direita)
    'tcMar',      # Margens internas / padding (top, bottom, left, right)
    'vAlign',     # Alinhamento vertical (top, center, bottom)
    'shd',        # Sombreamento / cor de fundo da célula
    'noWrap',     # Quebra de linha da célula
    'textDirection' # Direção do texto
]


def clone_cell_properties(src_cell, dst_cell, properties=None):
    """
    Copia propriedades OOXML da célula de origem para a célula de destino.
    Garante que linhas adicionadas dinamicamente tenham a mesma aparência do modelo.
    """
    if properties is None:
        properties = CLONEABLE_CELL_PROPERTIES

    src_tcPr = src_cell._tc.get_or_add_tcPr()
    dst_tcPr = dst_cell._tc.get_or_add_tcPr()

    for prop in properties:
        elem = src_tcPr.find(qn(f'w:{prop}'))
        if elem is not None:
            # Remove qualquer elemento existente do mesmo tipo no destino
            existing = dst_tcPr.find(qn(f'w:{prop}'))
            if existing is not None:
                dst_tcPr.remove(existing)
            # Clona em profundidade o elemento de estilo
            dst_tcPr.append(copy.deepcopy(elem))


def delete_paragraph_element(paragraph):
    """
    Remove fisicamente o nó do parágrafo do documento XML.
    Diferente de p.text = "", não deixa linhas ou quebras em branco residuais.
    """
    p_element = paragraph._element
    parent = p_element.getparent()
    if parent is not None:
        parent.remove(p_element)


def get_cell_text_clean(cell):
    """Retorna o texto de uma célula sem espaços ou quebras repetidas."""
    return " ".join(cell.text.split())
