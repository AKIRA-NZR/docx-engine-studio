"""
Módulo de Conversão Bidirecional: PDF <-> DOCX.
- PDF -> DOCX: Converte arquivos PDF em documentos Word editáveis com pdf2docx.
- DOCX -> PDF: Exporta documentos Word para PDF utilizando docx2pdf ou LibreOffice headless.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def pdf_to_docx(pdf_path: str, docx_path: Optional[str] = None) -> str:
    """
    Converte um documento PDF em arquivo DOCX editável.
    """
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {src}")

    if docx_path is None:
        dst = src.with_suffix(".docx")
    else:
        dst = Path(docx_path)

    dst.parent.mkdir(parents=True, exist_ok=True)

    from pdf2docx import Converter
    cv = Converter(str(src))
    try:
        cv.convert(str(dst), start=0, end=None)
    finally:
        cv.close()

    return str(dst)


def docx_to_pdf(docx_path: str, pdf_path: Optional[str] = None) -> str:
    """
    Converte um documento DOCX para PDF.
    Tenta primeiro via docx2pdf (Microsoft Word COM), e como fallback utiliza o LibreOffice headless.
    """
    src = Path(docx_path)
    if not src.exists():
        raise FileNotFoundError(f"Arquivo DOCX não encontrado: {src}")

    if pdf_path is None:
        dst = src.with_suffix(".pdf")
    else:
        dst = Path(pdf_path)

    dst.parent.mkdir(parents=True, exist_ok=True)

    # Tentativa 1: docx2pdf (requer MS Word no Windows)
    try:
        from docx2pdf import convert
        convert(str(src), str(dst))
        if dst.exists():
            return str(dst)
    except Exception:
        pass

    # Tentativa 2: Fallback para LibreOffice instalado na máquina
    libreoffice_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        shutil.which("soffice") or ""
    ]

    soffice_bin = next((p for p in libreoffice_paths if p and Path(p).exists()), None)
    if soffice_bin:
        out_dir = str(dst.parent.resolve())
        # Usa diretório de perfil isolado para não conflitar com janelas abertas do LibreOffice
        temp_profile = Path(os.environ.get("TEMP", ".")) / "lo_headless_profile"
        profile_arg = f"-env:UserInstallation=file:///{temp_profile.as_posix()}"

        cmd = [
            soffice_bin,
            "--headless",
            profile_arg,
            "--convert-to", "pdf:writer_pdf_Export",
            "--outdir", out_dir,
            str(src.resolve())
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        # O LibreOffice gera o PDF com o mesmo nome base do arquivo de entrada no diretório out_dir
        expected_lo_pdf = Path(out_dir) / f"{src.stem}.pdf"
        if expected_lo_pdf.exists():
            if expected_lo_pdf != dst:
                shutil.move(str(expected_lo_pdf), str(dst))
            return str(dst)

    raise RuntimeError(
        "Não foi possível converter DOCX para PDF. "
        "Certifique-se de que o Microsoft Word ou o LibreOffice esteja instalado."
    )
