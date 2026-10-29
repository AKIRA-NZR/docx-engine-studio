"""
Pacote docx_engine: Arquitetura extensível para automação e manipulação de documentos DOCX.
"""

from .editor import DocumentEditor
from .table_handler import TableHandler
from .paragraph_handler import ParagraphHandler
from .xml_utils import clone_cell_properties, delete_paragraph_element
from .validator import DocumentValidator, ValidationReport
from .converter import pdf_to_docx, docx_to_pdf

__all__ = [
    "DocumentEditor",
    "TableHandler",
    "ParagraphHandler",
    "DocumentValidator",
    "ValidationReport",
    "clone_cell_properties",
    "delete_paragraph_element",
    "pdf_to_docx",
    "docx_to_pdf"
]
