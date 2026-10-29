"""
Interface Gráfica Desktop Moderna (CustomTkinter / Tkinter)
para preenchimento, auditoria, validação e conversão de documentos DOCX e PDF.
"""

import os
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    BaseApp = ctk.CTk
except ImportError:
    import tkinter as ctk
    BaseApp = ctk.Tk

from docx_engine import DocumentEditor, pdf_to_docx, docx_to_pdf
from configs.mare_alerta_sprint4 import RECIPE_SPRINT_4


class DocxEngineStudio(BaseApp):
    def __init__(self):
        super().__init__()

        self.title("DOCX Engine Studio — Automação e Conversão de Documentos")
        self.geometry("920x680")
        self.minsize(800, 580)

        # Configuração de Layout Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        self._build_header()

        # Abas de Navegação
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_fill = self.tabview.add("📄 Preencher Relatório")
        self.tab_convert = self.tabview.add("🔄 Conversor PDF ↔ DOCX")
        self.tab_inspect = self.tabview.add("🔍 Inspecionar Modelo")

        self._build_tab_fill()
        self._build_tab_convert()
        self._build_tab_inspect()

        # Rodapé / Status
        self.status_bar = ctk.CTkLabel(
            self, text="Pronto para processar.", anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.status_bar.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

    # -------------------------------------------------------------------------
    # Cabeçalho
    # -------------------------------------------------------------------------
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        title_label = ctk.CTkLabel(
            header_frame,
            text="DOCX Engine Studio",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(side="left")

        subtitle = ctk.CTkLabel(
            header_frame,
            text=" |  Automação, Auditoria e Conversão de Documentos Word / LibreOffice",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle.pack(side="left", padx=5)

    # -------------------------------------------------------------------------
    # Aba 1: Preencher Relatório
    # -------------------------------------------------------------------------
    def _build_tab_fill(self):
        tab = self.tab_fill
        tab.grid_columnconfigure(1, weight=1)

        # Linha 1: Arquivo Modelo
        lbl_model = ctk.CTkLabel(tab, text="Modelo DOCX:", font=ctk.CTkFont(weight="bold"))
        lbl_model.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        default_model = "Modelo_Relatorio_de_Evolucao_de_Front-End.docx"
        self.entry_model = ctk.CTkEntry(tab)
        self.entry_model.insert(0, default_model if Path(default_model).exists() else "")
        self.entry_model.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        btn_browse_model = ctk.CTkButton(tab, text="Procurar...", width=100, command=self._browse_model)
        btn_browse_model.grid(row=0, column=2, padx=10, pady=8)

        # Linha 2: Arquivo de Saída
        lbl_out = ctk.CTkLabel(tab, text="Arquivo de Saída:", font=ctk.CTkFont(weight="bold"))
        lbl_out.grid(row=1, column=0, padx=10, pady=8, sticky="w")

        self.entry_output = ctk.CTkEntry(tab)
        self.entry_output.insert(0, "Relatorio_de_Evolucao_de_Front-End_Preenchido.docx")
        self.entry_output.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        btn_browse_out = ctk.CTkButton(tab, text="Definir...", width=100, command=self._browse_output)
        btn_browse_out.grid(row=1, column=2, padx=10, pady=8)

        # Linha 3: Receita / Dados
        lbl_recipe = ctk.CTkLabel(tab, text="Receita / Dados:", font=ctk.CTkFont(weight="bold"))
        lbl_recipe.grid(row=2, column=0, padx=10, pady=8, sticky="w")

        self.combo_recipe = ctk.CTkComboBox(
            tab,
            values=["Sprint 4 — Maré Alerta (Padrão)"]
        )
        self.combo_recipe.set("Sprint 4 — Maré Alerta (Padrão)")
        self.combo_recipe.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # Linha 4: Opções Adicionais
        opts_frame = ctk.CTkFrame(tab, fg_color="transparent")
        opts_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        self.check_pdf = ctk.CTkCheckBox(opts_frame, text="Exportar automaticamente para PDF")
        self.check_pdf.select()
        self.check_pdf.pack(side="left", padx=(0, 20))

        self.check_validate = ctk.CTkCheckBox(opts_frame, text="Auditar/Validar pendências antes de salvar")
        self.check_validate.select()
        self.check_validate.pack(side="left", padx=10)

        # Linha 5: Botões de Ação
        actions_frame = ctk.CTkFrame(tab, fg_color="transparent")
        actions_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.btn_run = ctk.CTkButton(
            actions_frame, text="▶ Gerar Documento",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f6aa5", hover_color="#144d75",
            command=self._start_fill_process
        )
        self.btn_run.pack(side="left", padx=(0, 10))

        self.btn_validate_only = ctk.CTkButton(
            actions_frame, text="🛡 Apenas Auditar",
            fg_color="#4a5568", hover_color="#2d3748",
            command=self._start_validation_only
        )
        self.btn_validate_only.pack(side="left", padx=10)

        self.btn_open = ctk.CTkButton(
            actions_frame, text="👁 Abrir Documento",
            fg_color="#2e7d32", hover_color="#1b5e20",
            command=self._open_generated_file
        )
        self.btn_open.pack(side="left", padx=10)

        # Linha 6: Console de Log
        self.txt_log = ctk.CTkTextbox(tab, height=180, font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_log.grid(row=5, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="nsew")
        tab.grid_rowconfigure(5, weight=1)

    # -------------------------------------------------------------------------
    # Aba 2: Conversor PDF <-> DOCX
    # -------------------------------------------------------------------------
    def _build_tab_convert(self):
        tab = self.tab_convert
        tab.grid_columnconfigure(1, weight=1)

        # Bloco A: PDF -> DOCX
        frame_pdf2docx = ctk.CTkFrame(tab)
        frame_pdf2docx.grid(row=0, column=0, columnspan=3, padx=10, pady=15, sticky="ew")
        frame_pdf2docx.grid_columnconfigure(1, weight=1)

        lbl_p2d_title = ctk.CTkLabel(frame_pdf2docx, text="Converter PDF para DOCX (Editável no Word/LibreOffice)", font=ctk.CTkFont(weight="bold", size=14))
        lbl_p2d_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

        lbl_pdf_in = ctk.CTkLabel(frame_pdf2docx, text="Arquivo PDF:")
        lbl_pdf_in.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.entry_pdf_in = ctk.CTkEntry(frame_pdf2docx)
        self.entry_pdf_in.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        btn_browse_pdf = ctk.CTkButton(frame_pdf2docx, text="Procurar...", width=100, command=self._browse_pdf_in)
        btn_browse_pdf.grid(row=1, column=2, padx=15, pady=8)

        self.btn_convert_p2d = ctk.CTkButton(
            frame_pdf2docx, text="🔄 Converter para DOCX",
            fg_color="#1f6aa5", hover_color="#144d75",
            command=self._run_pdf_to_docx
        )
        self.btn_convert_p2d.grid(row=2, column=1, padx=10, pady=(5, 15), sticky="w")

        # Bloco B: DOCX -> PDF
        frame_docx2pdf = ctk.CTkFrame(tab)
        frame_docx2pdf.grid(row=1, column=0, columnspan=3, padx=10, pady=15, sticky="ew")
        frame_docx2pdf.grid_columnconfigure(1, weight=1)

        lbl_d2p_title = ctk.CTkLabel(frame_docx2pdf, text="Exportar DOCX para PDF", font=ctk.CTkFont(weight="bold", size=14))
        lbl_d2p_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

        lbl_docx_in = ctk.CTkLabel(frame_docx2pdf, text="Arquivo DOCX:")
        lbl_docx_in.grid(row=1, column=0, padx=15, pady=8, sticky="w")

        self.entry_docx_in = ctk.CTkEntry(frame_docx2pdf)
        self.entry_docx_in.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        btn_browse_docx = ctk.CTkButton(frame_docx2pdf, text="Procurar...", width=100, command=self._browse_docx_in)
        btn_browse_docx.grid(row=1, column=2, padx=15, pady=8)

        self.btn_convert_d2p = ctk.CTkButton(
            frame_docx2pdf, text="📄 Exportar para PDF",
            fg_color="#2e7d32", hover_color="#1b5e20",
            command=self._run_docx_to_pdf
        )
        self.btn_convert_d2p.grid(row=2, column=1, padx=10, pady=(5, 15), sticky="w")

    # -------------------------------------------------------------------------
    # Aba 3: Inspecionar Modelo
    # -------------------------------------------------------------------------
    def _build_tab_inspect(self):
        tab = self.tab_inspect
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        lbl_insp = ctk.CTkLabel(tab, text="Documento DOCX:", font=ctk.CTkFont(weight="bold"))
        lbl_insp.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_insp = ctk.CTkEntry(tab)
        self.entry_insp.insert(0, "Modelo_Relatorio_de_Evolucao_de_Front-End.docx")
        self.entry_insp.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        btn_browse_insp = ctk.CTkButton(tab, text="Procurar...", width=100, command=self._browse_insp)
        btn_browse_insp.grid(row=0, column=2, padx=10, pady=10)

        btn_do_insp = ctk.CTkButton(tab, text="🔍 Inspecionar Estrutura", command=self._run_inspect)
        btn_do_insp.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")

        self.txt_insp_result = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_insp_result.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # -------------------------------------------------------------------------
    # Lógica e Eventos
    # -------------------------------------------------------------------------
    def _log(self, message):
        self.txt_log.insert("end", f"{message}\n")
        self.txt_log.see("end")

    def _set_status(self, text):
        self.status_bar.configure(text=text)

    def _browse_model(self):
        path = filedialog.askopenfilename(filetypes=[("Documentos Word", "*.docx")])
        if path:
            self.entry_model.delete(0, "end")
            self.entry_model.insert(0, path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Documentos Word", "*.docx")])
        if path:
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, path)

    def _browse_pdf_in(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if path:
            self.entry_pdf_in.delete(0, "end")
            self.entry_pdf_in.insert(0, path)

    def _browse_docx_in(self):
        path = filedialog.askopenfilename(filetypes=[("Documentos Word", "*.docx")])
        if path:
            self.entry_docx_in.delete(0, "end")
            self.entry_docx_in.insert(0, path)

    def _browse_insp(self):
        path = filedialog.askopenfilename(filetypes=[("Documentos Word", "*.docx")])
        if path:
            self.entry_insp.delete(0, "end")
            self.entry_insp.insert(0, path)

    def _start_fill_process(self):
        threading.Thread(target=self._process_document, daemon=True).start()

    def _process_document(self):
        model_path = self.entry_model.get().strip()
        out_path = self.entry_output.get().strip()

        if not Path(model_path).exists():
            messagebox.showerror("Erro", f"Modelo não encontrado: {model_path}")
            return

        self._set_status("Processando documento...")
        self._log(f"--- Iniciando preenchimento do modelo: {Path(model_path).name} ---")

        try:
            editor = DocumentEditor(model_path)
            editor.apply_recipe(RECIPE_SPRINT_4)

            # Auditoria prévia se ativada
            if self.check_validate.get():
                self._log("Executando auditoria do preenchimento...")
                report = editor.validate()
                self._log(report.summary())
                if not report.is_valid:
                    self._log("[AVISO] O relatório contém pendências apontadas acima.")

            saved_path = editor.save(out_path)
            self._log(f"[SUCESSO] Documento salvo em: {saved_path}")

            # Exportação PDF se ativada
            if self.check_pdf.get():
                self._set_status("Exportando para PDF...")
                self._log("Exportando cópia em PDF...")
                pdf_res = editor.export_pdf(output_docx_path=saved_path)
                self._log(f"[SUCESSO] PDF gerado em: {pdf_res}")

            self._set_status("Concluído com sucesso!")
            messagebox.showinfo("Sucesso", f"Documento gerado com sucesso!\nSalvo em:\n{saved_path}")
        except Exception as e:
            self._set_status("Erro durante a execução.")
            self._log(f"[ERRO] {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def _start_validation_only(self):
        model_path = self.entry_output.get().strip()
        if not Path(model_path).exists():
            model_path = self.entry_model.get().strip()

        if not Path(model_path).exists():
            messagebox.showerror("Erro", "Nenhum arquivo encontrado para auditar.")
            return

        try:
            editor = DocumentEditor(model_path)
            report = editor.validate()
            self._log(f"--- Auditoria isolada do arquivo: {Path(model_path).name} ---")
            self._log(report.summary())
            messagebox.showinfo("Auditoria", f"Auditoria concluída!\nPendências: {report.total_issues} ({len(report.errors)} erros críticos).")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na auditoria: {str(e)}")

    def _open_generated_file(self):
        target = self.entry_output.get().strip()
        if not Path(target).exists():
            target = "Relatorio_de_Evolucao_de_Front-End_Preenchido.docx"

        if Path(target).exists():
            os.startfile(str(Path(target).resolve()))
        else:
            messagebox.showwarning("Aviso", f"Arquivo não encontrado: {target}")

    def _run_pdf_to_docx(self):
        pdf_path = self.entry_pdf_in.get().strip()
        if not Path(pdf_path).exists():
            messagebox.showerror("Erro", "Selecione um arquivo PDF válido.")
            return

        self._set_status("Convertendo PDF para DOCX...")
        def task():
            try:
                docx_out = pdf_to_docx(pdf_path)
                self._set_status("Conversão concluída!")
                messagebox.showinfo("Sucesso", f"PDF convertido com sucesso para:\n{docx_out}")
            except Exception as e:
                self._set_status("Erro na conversão.")
                messagebox.showerror("Erro", f"Falha ao converter PDF: {str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def _run_docx_to_pdf(self):
        docx_path = self.entry_docx_in.get().strip()
        if not Path(docx_path).exists():
            messagebox.showerror("Erro", "Selecione um arquivo DOCX válido.")
            return

        self._set_status("Exportando DOCX para PDF...")
        def task():
            try:
                pdf_out = docx_to_pdf(docx_path)
                self._set_status("Exportação concluída!")
                messagebox.showinfo("Sucesso", f"DOCX exportado com sucesso para:\n{pdf_out}")
            except Exception as e:
                self._set_status("Erro na exportação.")
                messagebox.showerror("Erro", f"Falha ao exportar PDF: {str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def _run_inspect(self):
        path = self.entry_insp.get().strip()
        if not Path(path).exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado: {path}")
            return

        try:
            editor = DocumentEditor(path)
            lines = [
                f"Estrutura do Modelo: {Path(path).name}",
                f"Total de parágrafos: {len(editor.doc.paragraphs)}",
                f"Total de tabelas: {len(editor.doc.tables)}",
                "",
                "--- Tabelas Encontradas ---"
            ]
            for idx, table in enumerate(editor.doc.tables):
                headers = [c.text.strip().replace("\n", " ") for c in table.rows[0].cells[:4]] if table.rows else []
                lines.append(f"Tabela #{idx}: {len(table.rows)} linhas, {len(table.columns)} colunas. Cabeçalhos: {headers}")

            self.txt_insp_result.delete("1.0", "end")
            self.txt_insp_result.insert("1.0", "\n".join(lines))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao inspecionar: {str(e)}")


def main():
    app = DocxEngineStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
