"""
Ponto de entrada principal da arquitetura de automação de documentos DOCX.
Permite inspecionar modelos desconhecidos e aplicar transformações via CLI ou código.
"""

import argparse
import sys
from pathlib import Path

from docx_engine import DocumentEditor
from configs.exemplo_relatorio import RECIPE_EXEMPLO


def run_default():
    """Execução padrão do relatório de exemplo utilizando a arquitetura."""
    template_file = "Modelo_Relatorio_de_Evolucao_de_Front-End.docx"
    output_file = "Relatorio_de_Evolucao_de_Front-End_Preenchido.docx"

    print("Iniciando motor de transformação de documentos DOCX...")
    editor = DocumentEditor(template_file)
    editor.apply_recipe(RECIPE_EXEMPLO)
    saved_path = editor.save(output_file)
    print(f"Sucesso! Relatório gerado em: {saved_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Motor extensível de automação e transformação de documentos DOCX."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspeciona tabelas e parágrafos de um modelo DOCX")
    inspect_parser.add_argument("file", help="Caminho do arquivo DOCX para inspeção")

    # Comando: run
    run_parser = subparsers.add_parser("run", help="Executa o preenchimento de um documento")
    run_parser.add_argument("--template", "-t", default="Modelo_Relatorio_de_Evolucao_de_Front-End.docx", help="Modelo DOCX")
    run_parser.add_argument("--output", "-o", default="Relatorio_de_Evolucao_de_Front-End_Preenchido.docx", help="Arquivo DOCX de saída")

    args = parser.parse_args()

    if args.command == "inspect":
        editor = DocumentEditor(args.file)
        editor.inspect()
    elif args.command == "run":
        editor = DocumentEditor(args.template)
        editor.apply_recipe(RECIPE_EXEMPLO)
        editor.save(args.output)
    else:
        # Sem argumentos: executa o fluxo padrão
        run_default()


if __name__ == "__main__":
    main()
