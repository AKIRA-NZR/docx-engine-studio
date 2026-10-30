import React, { useEffect, useState } from 'react';
import {
  FileText,
  ShieldCheck,
  RefreshCw,
  Search,
  Upload,
  Download,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Play,
  FileOutput,
  Sparkles,
  RotateCcw,
} from 'lucide-react';
import './App.css';
import type {
  ConvertResult,
  DocumentInspection,
  ProcessResult,
  ValidationReportData,
} from './types';

type ActiveTab = 'automate' | 'validate' | 'convert' | 'inspect';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('automate');
  const [apiOnline, setApiOnline] = useState<boolean>(true);
  const [defaultTemplateName, setDefaultTemplateName] = useState<string>('Modelo padrão');

  // --- State: Automate Tab ---
  const [autoFile, setAutoFile] = useState<File | null>(null);
  const [recipeText, setRecipeText] = useState<string>('');
  const [defaultRecipeText, setDefaultRecipeText] = useState<string>('');
  const [exportPdf, setExportPdf] = useState<boolean>(true);
  const [validateAfter, setValidateAfter] = useState<boolean>(true);
  const [autoLoading, setAutoLoading] = useState<boolean>(false);
  const [autoError, setAutoError] = useState<string | null>(null);
  const [processResult, setProcessResult] = useState<ProcessResult | null>(null);

  // --- State: Validate Tab ---
  const [valFile, setValFile] = useState<File | null>(null);
  const [checkEmptyCells, setCheckEmptyCells] = useState<boolean>(false);
  const [valLoading, setValLoading] = useState<boolean>(false);
  const [valError, setValError] = useState<string | null>(null);
  const [valReport, setValReport] = useState<ValidationReportData | null>(null);

  // --- State: Convert Tab ---
  const [pdfInputFile, setPdfInputFile] = useState<File | null>(null);
  const [p2dLoading, setP2dLoading] = useState<boolean>(false);
  const [p2dResult, setP2dResult] = useState<ConvertResult | null>(null);
  const [p2dError, setP2dError] = useState<string | null>(null);

  const [docxInputFile, setDocxInputFile] = useState<File | null>(null);
  const [d2pLoading, setD2pLoading] = useState<boolean>(false);
  const [d2pResult, setD2pResult] = useState<ConvertResult | null>(null);
  const [d2pError, setD2pError] = useState<string | null>(null);

  // --- State: Inspect Tab ---
  const [inspFile, setInspFile] = useState<File | null>(null);
  const [inspLoading, setInspLoading] = useState<boolean>(false);
  const [inspError, setInspError] = useState<string | null>(null);
  const [inspection, setInspection] = useState<DocumentInspection | null>(null);

  useEffect(() => {
    fetch('/api/default-recipe')
      .then((res) => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then((data) => {
        setApiOnline(true);
        const formatted = JSON.stringify(data.recipe, null, 2);
        setRecipeText(formatted);
        setDefaultRecipeText(formatted);
        if (data.default_template) {
          setDefaultTemplateName(data.default_template);
        }
      })
      .catch(() => {
        setApiOnline(false);
      });
  }, []);

  // --- Handlers ---
  const handleRunAutomation = async () => {
    setAutoLoading(true);
    setAutoError(null);
    setProcessResult(null);

    try {
      const formData = new FormData();
      if (autoFile) {
        formData.append('file', autoFile);
      }
      formData.append('recipe_json', recipeText);
      formData.append('export_pdf', String(exportPdf));
      formData.append('validate_after', String(validateAfter));

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Falha ao processar documento.');
      }
      setProcessResult(data);
    } catch (err: any) {
      setAutoError(err.message || 'Erro desconhecido.');
    } finally {
      setAutoLoading(false);
    }
  };

  const handleRunValidation = async () => {
    setValLoading(true);
    setValError(null);
    setValReport(null);

    try {
      const formData = new FormData();
      if (valFile) {
        formData.append('file', valFile);
      }
      formData.append('check_empty_cells', String(checkEmptyCells));

      const response = await fetch('/api/validate', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao validar documento.');
      }
      setValReport(data);
    } catch (err: any) {
      setValError(err.message || 'Erro ao executar validação.');
    } finally {
      setValLoading(false);
    }
  };

  const handlePdfToDocx = async () => {
    if (!pdfInputFile) return;
    setP2dLoading(true);
    setP2dError(null);
    setP2dResult(null);

    try {
      const formData = new FormData();
      formData.append('file', pdfInputFile);
      const res = await fetch('/api/convert/pdf-to-docx', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao converter PDF.');
      setP2dResult(data);
    } catch (err: any) {
      setP2dError(err.message || 'Erro na conversão.');
    } finally {
      setP2dLoading(false);
    }
  };

  const handleDocxToPdf = async () => {
    if (!docxInputFile) return;
    setD2pLoading(true);
    setD2pError(null);
    setD2pResult(null);

    try {
      const formData = new FormData();
      formData.append('file', docxInputFile);
      const res = await fetch('/api/convert/docx-to-pdf', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao exportar PDF.');
      setD2pResult(data);
    } catch (err: any) {
      setD2pError(err.message || 'Erro na exportação.');
    } finally {
      setD2pLoading(false);
    }
  };

  const handleInspect = async () => {
    setInspLoading(true);
    setInspError(null);
    setInspection(null);

    try {
      const formData = new FormData();
      if (inspFile) {
        formData.append('file', inspFile);
      }
      const res = await fetch('/api/inspect', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Falha ao inspecionar documento.');
      setInspection(data);
    } catch (err: any) {
      setInspError(err.message || 'Erro ao inspecionar.');
    } finally {
      setInspLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={24} />
          </div>
          <div>
            <h1>DOCX Engine Studio</h1>
            <p>Automação de Modificações, Auditoria de Conformidade e Conversão PDF ↔ DOCX</p>
          </div>
        </div>
        <div className={`status-badge ${apiOnline ? '' : 'offline'}`}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: apiOnline ? '#34d399' : '#f87171',
            }}
          />
          {apiOnline ? 'Motor Python Conectado' : 'API Backend Offline (Inicie api_server.py)'}
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button
          className={`tab-btn ${activeTab === 'automate' ? 'active' : ''}`}
          onClick={() => setActiveTab('automate')}
        >
          <FileText size={18} />
          Automação & Preenchimento
        </button>
        <button
          className={`tab-btn ${activeTab === 'validate' ? 'active' : ''}`}
          onClick={() => setActiveTab('validate')}
        >
          <ShieldCheck size={18} />
          Auditor & Validador
        </button>
        <button
          className={`tab-btn ${activeTab === 'convert' ? 'active' : ''}`}
          onClick={() => setActiveTab('convert')}
        >
          <RefreshCw size={18} />
          Conversor PDF ↔ DOCX
        </button>
        <button
          className={`tab-btn ${activeTab === 'inspect' ? 'active' : ''}`}
          onClick={() => setActiveTab('inspect')}
        >
          <Search size={18} />
          Inspetor de Estrutura
        </button>
      </nav>

      {/* TAB 1: AUTOMATION */}
      {activeTab === 'automate' && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">
              <FileText size={20} color="#3b82f6" />
              Configuração da Transformação
            </div>
            <p className="card-subtitle">
              Envie qualquer arquivo .docx (ou utilize o modelo padrão) e defina as regras de preenchimento.
            </p>

            <label className="upload-box">
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setAutoFile(e.target.files?.[0] || null)}
              />
              <Upload size={26} color="#3b82f6" />
              <div className="upload-title">
                {autoFile ? autoFile.name : `Usando padrão: ${defaultTemplateName}`}
              </div>
              <div className="upload-hint">
                Clique para selecionar outro arquivo .docx do computador
              </div>
            </label>

            <div className="form-group">
              <div className="form-label">
                <span>Receita Declarativa (JSON)</span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ padding: '4px 10px', fontSize: '0.76rem' }}
                  onClick={() => setRecipeText(defaultRecipeText)}
                >
                  <RotateCcw size={13} /> Restaurar Exemplo
                </button>
              </div>
              <textarea
                className="json-editor"
                value={recipeText}
                onChange={(e) => setRecipeText(e.target.value)}
                spellCheck={false}
              />
            </div>

            <div className="checkbox-row">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={validateAfter}
                  onChange={(e) => setValidateAfter(e.target.checked)}
                />
                Auditar pendências após modificar
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={exportPdf}
                  onChange={(e) => setExportPdf(e.target.checked)}
                />
                Exportar automaticamente para PDF
              </label>
            </div>

            <div className="btn-row">
              <button
                className="btn btn-primary"
                onClick={handleRunAutomation}
                disabled={autoLoading}
              >
                <Play size={17} />
                {autoLoading ? 'Processando Documento...' : 'Executar Automação'}
              </button>
            </div>
          </div>

          <div className="card">
            <div className="card-title">
              <FileOutput size={20} color="#10b981" />
              Resultado & Downloads
            </div>
            <p className="card-subtitle">
              Arquivos gerados com preservação total de bordas OOXML e relatório de conformidade.
            </p>

            {autoError && (
              <div className="alert-banner alert-error">
                <XCircle size={20} style={{ flexShrink: 0 }} />
                <div>{autoError}</div>
              </div>
            )}

            {!processResult && !autoError && (
              <div
                style={{
                  textAlign: 'center',
                  padding: '60px 20px',
                  color: 'var(--text-muted)',
                }}
              >
                <FileText size={42} style={{ opacity: 0.35, marginBottom: 12 }} />
                <p>Clique em "Executar Automação" para processar e gerar os arquivos.</p>
              </div>
            )}

            {processResult && (
              <div>
                <div className="alert-banner alert-success">
                  <CheckCircle2 size={20} style={{ flexShrink: 0 }} />
                  <div>
                    <strong>Documento processado com sucesso!</strong>
                    <div style={{ marginTop: 4, fontSize: '0.82rem' }}>
                      Todas as tabelas, variáveis e parágrafos foram transformados.
                    </div>
                  </div>
                </div>

                <div className="btn-row" style={{ marginBottom: 24 }}>
                  <a
                    href={processResult.docx_download_url}
                    download
                    className="btn btn-primary"
                  >
                    <Download size={17} />
                    Baixar DOCX ({processResult.docx_filename})
                  </a>

                  {processResult.pdf_download_url && (
                    <a
                      href={processResult.pdf_download_url}
                      download
                      className="btn btn-success"
                    >
                      <Download size={17} />
                      Baixar PDF ({processResult.pdf_filename})
                    </a>
                  )}
                </div>

                {processResult.pdf_error && (
                  <div className="alert-banner alert-warning">
                    <AlertTriangle size={18} style={{ flexShrink: 0 }} />
                    <div>Aviso na exportação PDF: {processResult.pdf_error}</div>
                  </div>
                )}

                {processResult.validation && (
                  <div style={{ marginTop: 16 }}>
                    <h4 style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                      Relatório de Auditoria Automática
                    </h4>
                    <div className="stats-grid">
                      <div className="stat-card">
                        <div
                          className="stat-val"
                          style={{
                            color: processResult.validation.is_valid
                              ? 'var(--success)'
                              : 'var(--danger)',
                          }}
                        >
                          {processResult.validation.is_valid ? 'APROVADO' : 'PENDENTE'}
                        </div>
                        <div className="stat-lbl">Status Geral</div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-val">{processResult.validation.errors.length}</div>
                        <div className="stat-lbl">Erros Críticos</div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-val">{processResult.validation.warnings.length}</div>
                        <div className="stat-lbl">Avisos</div>
                      </div>
                    </div>

                    {processResult.validation.errors.length > 0 && (
                      <div className="issue-list">
                        {processResult.validation.errors.map((err, i) => (
                          <div key={i} className="issue-item">
                            <div className="issue-loc">{err.location}</div>
                            <div>{err.message}</div>
                            {err.snippet && <div className="issue-snippet">{err.snippet}</div>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: VALIDATOR */}
      {activeTab === 'validate' && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">
              <ShieldCheck size={20} color="#3b82f6" />
              Auditoria de Preenchimento
            </div>
            <p className="card-subtitle">
              Analisa qualquer arquivo .docx em busca de linhas pontilhadas esquecidas (____), tags {'{{pendentes}}'} ou células em branco.
            </p>

            <label className="upload-box">
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setValFile(e.target.files?.[0] || null)}
              />
              <Upload size={26} color="#3b82f6" />
              <div className="upload-title">
                {valFile ? valFile.name : `Auditar modelo: ${defaultTemplateName}`}
              </div>
              <div className="upload-hint">
                Selecione um arquivo .docx preenchido ou em branco para testar o validador
              </div>
            </label>

            <div className="checkbox-row">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={checkEmptyCells}
                  onChange={(e) => setCheckEmptyCells(e.target.checked)}
                />
                Alertar também sobre células de tabelas vazias
              </label>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleRunValidation}
              disabled={valLoading}
            >
              <ShieldCheck size={17} />
              {valLoading ? 'Auditando...' : 'Executar Auditoria'}
            </button>
          </div>

          <div className="card">
            <div className="card-title">Diagnóstico do Documento</div>
            <p className="card-subtitle">Resultado detalhado da verificação de conformidade.</p>

            {valError && (
              <div className="alert-banner alert-error">
                <XCircle size={20} />
                <div>{valError}</div>
              </div>
            )}

            {valReport && (
              <div>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div
                      className="stat-val"
                      style={{
                        color: valReport.is_valid ? 'var(--success)' : 'var(--danger)',
                      }}
                    >
                      {valReport.is_valid ? '100% OK' : 'PENDENTE'}
                    </div>
                    <div className="stat-lbl">Conformidade</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val">{valReport.errors.length}</div>
                    <div className="stat-lbl">Placeholders / Tags Sem Resposta</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val">{valReport.warnings.length}</div>
                    <div className="stat-lbl">Células Vazias / Avisos</div>
                  </div>
                </div>

                <div className="issue-list">
                  {valReport.errors.map((err, idx) => (
                    <div key={`e-${idx}`} className="issue-item">
                      <div className="issue-loc">❌ {err.location}</div>
                      <div>{err.message}</div>
                      {err.snippet && <div className="issue-snippet">{err.snippet}</div>}
                    </div>
                  ))}
                  {valReport.warnings.map((warn, idx) => (
                    <div key={`w-${idx}`} className="issue-item warning">
                      <div className="issue-loc">⚠️ {warn.location}</div>
                      <div>{warn.message}</div>
                    </div>
                  ))}
                  {valReport.errors.length === 0 && valReport.warnings.length === 0 && (
                    <div className="alert-banner alert-success">
                      <CheckCircle2 size={20} />
                      <div>Nenhuma pendência encontrada! O documento está pronto para entrega.</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: CONVERTER */}
      {activeTab === 'convert' && (
        <div className="grid-2">
          {/* PDF -> DOCX */}
          <div className="card">
            <div className="card-title">
              <RefreshCw size={20} color="#3b82f6" />
              Converter PDF para Word (.docx)
            </div>
            <p className="card-subtitle">
              Reconstrói parágrafos, tabelas e layout de um arquivo PDF em um documento .docx editável via pdf2docx.
            </p>

            <label className="upload-box">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setPdfInputFile(e.target.files?.[0] || null)}
              />
              <Upload size={26} color="#3b82f6" />
              <div className="upload-title">
                {pdfInputFile ? pdfInputFile.name : 'Selecione um arquivo .pdf'}
              </div>
              <div className="upload-hint">Clique para escolher o PDF que deseja converter</div>
            </label>

            <button
              className="btn btn-primary"
              onClick={handlePdfToDocx}
              disabled={!pdfInputFile || p2dLoading}
            >
              <RefreshCw size={17} />
              {p2dLoading ? 'Convertendo PDF...' : 'Converter em DOCX'}
            </button>

            {p2dError && (
              <div className="alert-banner alert-error" style={{ marginTop: 16 }}>
                <XCircle size={18} />
                <div>{p2dError}</div>
              </div>
            )}

            {p2dResult && (
              <div className="alert-banner alert-success" style={{ marginTop: 16 }}>
                <CheckCircle2 size={20} />
                <div style={{ flex: 1 }}>
                  <div>
                    <strong>Conversão concluída!</strong>
                  </div>
                  <a
                    href={p2dResult.download_url}
                    download
                    className="btn btn-primary"
                    style={{ marginTop: 10 }}
                  >
                    <Download size={16} />
                    Baixar {p2dResult.filename}
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* DOCX -> PDF */}
          <div className="card">
            <div className="card-title">
              <FileOutput size={20} color="#10b981" />
              Exportar Word (.docx) para PDF
            </div>
            <p className="card-subtitle">
              Converte qualquer documento .docx para formato PDF final utilizando Word COM ou LibreOffice Headless.
            </p>

            <label className="upload-box">
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setDocxInputFile(e.target.files?.[0] || null)}
              />
              <Upload size={26} color="#10b981" />
              <div className="upload-title">
                {docxInputFile ? docxInputFile.name : 'Selecione um arquivo .docx'}
              </div>
              <div className="upload-hint">Clique para escolher o DOCX que deseja exportar</div>
            </label>

            <button
              className="btn btn-success"
              onClick={handleDocxToPdf}
              disabled={!docxInputFile || d2pLoading}
            >
              <FileOutput size={17} />
              {d2pLoading ? 'Exportando para PDF...' : 'Exportar para PDF'}
            </button>

            {d2pError && (
              <div className="alert-banner alert-error" style={{ marginTop: 16 }}>
                <XCircle size={18} />
                <div>{d2pError}</div>
              </div>
            )}

            {d2pResult && (
              <div className="alert-banner alert-success" style={{ marginTop: 16 }}>
                <CheckCircle2 size={20} />
                <div style={{ flex: 1 }}>
                  <div>
                    <strong>PDF gerado com sucesso!</strong>
                  </div>
                  <a
                    href={d2pResult.download_url}
                    download
                    className="btn btn-success"
                    style={{ marginTop: 10 }}
                  >
                    <Download size={16} />
                    Baixar {d2pResult.filename}
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: INSPECT */}
      {activeTab === 'inspect' && (
        <div className="grid-2">
          <div className="card">
            <div className="card-title">
              <Search size={20} color="#3b82f6" />
              Inspetor Estrutural de Modelos
            </div>
            <p className="card-subtitle">
              Descubra os cabeçalhos das tabelas e parágrafos de qualquer documento .docx para criar receitas de automação.
            </p>

            <label className="upload-box">
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setInspFile(e.target.files?.[0] || null)}
              />
              <Upload size={26} color="#3b82f6" />
              <div className="upload-title">
                {inspFile ? inspFile.name : `Inspecionar padrão: ${defaultTemplateName}`}
              </div>
              <div className="upload-hint">Clique para carregar qualquer modelo .docx</div>
            </label>

            <button
              className="btn btn-primary"
              onClick={handleInspect}
              disabled={inspLoading}
            >
              <Search size={17} />
              {inspLoading ? 'Mapeando...' : 'Inspecionar Documento'}
            </button>

            {inspError && (
              <div className="alert-banner alert-error" style={{ marginTop: 16 }}>
                <XCircle size={18} />
                <div>{inspError}</div>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title">Mapeamento de Tabelas e Cabeçalhos</div>
            <p className="card-subtitle">
              Use os cabeçalhos abaixo para preencher tabelas de forma semântica na sua receita.
            </p>

            {inspection && (
              <div>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-val">{inspection.total_tables}</div>
                    <div className="stat-lbl">Tabelas</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val">{inspection.total_paragraphs}</div>
                    <div className="stat-lbl">Parágrafos Totais</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-val">{inspection.non_empty_paragraphs}</div>
                    <div className="stat-lbl">Parágrafos com Texto</div>
                  </div>
                </div>

                <div className="table-list">
                  {inspection.tables.map((t) => (
                    <div key={t.index} className="table-inspect-item">
                      <div className="table-inspect-header">
                        <span>Tabela #{t.index}</span>
                        <span className="tag-pill">
                          {t.rows} linhas × {t.columns} colunas
                        </span>
                      </div>
                      <div className="headers-wrap">
                        {t.headers.map((h, i) => (
                          <span key={i} className="header-chip">
                            {h || '(vazio)'}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
export default App;
