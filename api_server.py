"""
Servidor de API REST (FastAPI) para o DOCX Engine Studio.
Conecta o frontend React + TypeScript ao motor Python de automação, validação e conversão.
"""

import json
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from configs.exemplo_relatorio import RECIPE_EXEMPLO
from docx_engine import DocumentEditor, docx_to_pdf, pdf_to_docx

app = FastAPI(
    title="DOCX Engine Studio API",
    description="API para automação de modificações, auditoria e conversão bidirecional de documentos DOCX e PDF.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

DEFAULT_TEMPLATE = BASE_DIR / "Modelo_Relatorio_de_Evolucao_de_Front-End.docx"


def _resolve_template_file(upload: Optional[UploadFile]) -> Path:
    """Salva o upload recebido ou utiliza o modelo padrão do repositório."""
    if upload and upload.filename:
        ext = Path(upload.filename).suffix or ".docx"
        temp_path = OUTPUTS_DIR / f"upload_{uuid.uuid4().hex[:8]}{ext}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        return temp_path

    if DEFAULT_TEMPLATE.exists():
        return DEFAULT_TEMPLATE

    raise HTTPException(status_code=400, detail="Nenhum arquivo enviado e modelo padrão não encontrado.")


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "default_template_available": DEFAULT_TEMPLATE.exists(),
        "default_template_name": DEFAULT_TEMPLATE.name if DEFAULT_TEMPLATE.exists() else None,
    }


@app.get("/api/default-recipe")
def get_default_recipe():
    return {
        "recipe": RECIPE_EXEMPLO,
        "default_template": DEFAULT_TEMPLATE.name if DEFAULT_TEMPLATE.exists() else None,
    }


@app.post("/api/inspect")
def inspect_document(file: Optional[UploadFile] = File(None)):
    target_path = _resolve_template_file(file)
    try:
        editor = DocumentEditor(target_path)
        tables_info = []
        for idx, table in enumerate(editor.doc.tables):
            headers = [c.text.strip().replace("\n", " ") for c in table.rows[0].cells] if table.rows else []
            sample_rows = []
            for r in table.rows[1:4]:
                sample_rows.append([c.text.strip().replace("\n", " ") for c in r.cells])
            tables_info.append({
                "index": idx,
                "rows": len(table.rows),
                "columns": len(table.columns),
                "headers": headers,
                "sample_rows": sample_rows,
            })

        paragraphs_info = [
            {"index": i, "text": p.text.strip()}
            for i, p in enumerate(editor.doc.paragraphs)
            if p.text.strip()
        ]

        return {
            "filename": file.filename if (file and file.filename) else DEFAULT_TEMPLATE.name,
            "total_paragraphs": len(editor.doc.paragraphs),
            "non_empty_paragraphs": len(paragraphs_info),
            "total_tables": len(editor.doc.tables),
            "tables": tables_info,
            "paragraphs": paragraphs_info[:60],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao inspecionar documento: {str(e)}")


@app.post("/api/validate")
def validate_document(
    file: Optional[UploadFile] = File(None),
    check_empty_cells: bool = Form(False),
):
    target_path = _resolve_template_file(file)
    try:
        editor = DocumentEditor(target_path)
        report = editor.validate(check_empty_cells=check_empty_cells)
        return {
            "filename": file.filename if (file and file.filename) else DEFAULT_TEMPLATE.name,
            "is_valid": report.is_valid,
            "total_issues": report.total_issues,
            "errors": [
                {
                    "category": err.category,
                    "location": err.location,
                    "message": err.message,
                    "severity": err.severity,
                    "snippet": err.snippet,
                }
                for err in report.errors
            ],
            "warnings": [
                {
                    "category": w.category,
                    "location": w.location,
                    "message": w.message,
                    "severity": w.severity,
                    "snippet": w.snippet,
                }
                for w in report.warnings
            ],
            "summary": report.summary(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na auditoria: {str(e)}")


@app.post("/api/process")
def process_document(
    file: Optional[UploadFile] = File(None),
    recipe_json: Optional[str] = Form(None),
    export_pdf: bool = Form(False),
    validate_after: bool = Form(True),
):
    target_path = _resolve_template_file(file)
    try:
        recipe = json.loads(recipe_json) if recipe_json else RECIPE_EXEMPLO
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON de receita inválido: {str(e)}")

    try:
        editor = DocumentEditor(target_path)
        editor.apply_recipe(recipe)

        run_id = uuid.uuid4().hex[:8]
        base_stem = Path(file.filename).stem if (file and file.filename) else "Documento_Automatizado"
        out_docx_name = f"{base_stem}_{run_id}.docx"
        out_docx_path = OUTPUTS_DIR / out_docx_name

        saved_docx = Path(editor.save(out_docx_path))

        validation_data = None
        if validate_after:
            report = editor.validate()
            validation_data = {
                "is_valid": report.is_valid,
                "total_issues": report.total_issues,
                "errors": [
                    {
                        "category": err.category,
                        "location": err.location,
                        "message": err.message,
                        "severity": err.severity,
                        "snippet": err.snippet,
                    }
                    for err in report.errors
                ],
                "warnings": [
                    {
                        "category": w.category,
                        "location": w.location,
                        "message": w.message,
                        "severity": w.severity,
                        "snippet": w.snippet,
                    }
                    for w in report.warnings
                ],
                "summary": report.summary(),
            }

        pdf_filename = None
        pdf_error = None
        if export_pdf:
            try:
                out_pdf_name = f"{base_stem}_{run_id}.pdf"
                out_pdf_path = OUTPUTS_DIR / out_pdf_name
                saved_pdf = Path(docx_to_pdf(str(saved_docx), str(out_pdf_path)))
                pdf_filename = saved_pdf.name
            except Exception as pe:
                pdf_error = str(pe)

        return {
            "status": "success",
            "docx_filename": saved_docx.name,
            "docx_download_url": f"/api/download/{saved_docx.name}",
            "pdf_filename": pdf_filename,
            "pdf_download_url": f"/api/download/{pdf_filename}" if pdf_filename else None,
            "pdf_error": pdf_error,
            "validation": validation_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")


@app.post("/api/convert/pdf-to-docx")
def convert_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Por favor, envie um arquivo .pdf válido.")

    run_id = uuid.uuid4().hex[:8]
    stem = Path(file.filename).stem
    in_pdf = OUTPUTS_DIR / f"{stem}_{run_id}.pdf"
    out_docx = OUTPUTS_DIR / f"{stem}_convertido_{run_id}.docx"

    with open(in_pdf, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result_path = Path(pdf_to_docx(str(in_pdf), str(out_docx)))
        return {
            "status": "success",
            "filename": result_path.name,
            "download_url": f"/api/download/{result_path.name}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao converter PDF para DOCX: {str(e)}")


@app.post("/api/convert/docx-to-pdf")
def convert_docx_endpoint(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Por favor, envie um arquivo .docx válido.")

    run_id = uuid.uuid4().hex[:8]
    stem = Path(file.filename).stem
    in_docx = OUTPUTS_DIR / f"{stem}_{run_id}.docx"
    out_pdf = OUTPUTS_DIR / f"{stem}_exportado_{run_id}.pdf"

    with open(in_docx, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result_path = Path(docx_to_pdf(str(in_docx), str(out_pdf)))
        return {
            "status": "success",
            "filename": result_path.name,
            "download_url": f"/api/download/{result_path.name}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao exportar DOCX para PDF: {str(e)}")


@app.get("/api/download/{filename}")
def download_file(filename: str):
    safe_name = Path(filename).name
    file_path = OUTPUTS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(path=str(file_path), filename=safe_name)


FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
