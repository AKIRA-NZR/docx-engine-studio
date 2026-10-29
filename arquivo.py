"""
arquivo.py: Refatorado para utilizar a arquitetura modular docx_engine.
Mantém compatibilidade com a execução direta: `python arquivo.py`.
"""

from docx_engine import DocumentEditor
from configs.exemplo_relatorio import RECIPE_EXEMPLO

def main():
    template = "Modelo_Relatorio_de_Evolucao_de_Front-End.docx"
    output = "Relatorio_de_Evolucao_de_Front-End_Preenchido.docx"

    print("Carregando modelo e aplicando transformações com a nova arquitetura...")
    editor = DocumentEditor(template)
    
    # Aplica a receita declarativa completa (tabelas, textos, checkboxes e formatação)
    editor.apply_recipe(RECIPE_EXEMPLO)
    
    # Salva com proteção contra travamento por arquivos abertos no LibreOffice/Word
    editor.save(output)

if __name__ == "__main__":
    main()
