export interface ValidationIssue {
  category: string;
  location: string;
  message: string;
  severity: 'error' | 'warning';
  snippet: string;
}

export interface ValidationReportData {
  filename?: string;
  is_valid: boolean;
  total_issues: number;
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  summary: string;
}

export interface TableInspectInfo {
  index: number;
  rows: number;
  columns: number;
  headers: string[];
  sample_rows: string[][];
}

export interface DocumentInspection {
  filename: string;
  total_paragraphs: number;
  non_empty_paragraphs: number;
  total_tables: number;
  tables: TableInspectInfo[];
  paragraphs: { index: number; text: string }[];
}

export interface ProcessResult {
  status: string;
  docx_filename: string;
  docx_download_url: string;
  pdf_filename: string | null;
  pdf_download_url: string | null;
  pdf_error: string | null;
  validation: ValidationReportData | null;
}

export interface ConvertResult {
  status: string;
  filename: string;
  download_url: string;
}
