import { Case, Field, Finding, AuditEvent, Document } from '../types';

const BACKEND_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const API_BASE = `${BACKEND_URL}/api`;

export async function fetchHealth() {
  const res = await fetch(`${BACKEND_URL}/health/ready`);
  return res.json();
}

export async function fetchCapabilities() {
  const res = await fetch(`${BACKEND_URL}/capabilities`);
  return res.json();
}

export async function fetchCases(): Promise<Case[]> {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) throw new Error('Failed to fetch cases');
  return res.json();
}

export async function createCase(data: { reference_number: string; applicant_name: string }): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create case');
  }
  return res.json();
}

export async function fetchCase(caseId: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) throw new Error('Failed to fetch case details');
  return res.json();
}

export async function uploadDocuments(caseId: string, files: File[]): Promise<Document[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const res = await fetch(`${API_BASE}/cases/${caseId}/documents`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail?.message || err.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function fetchCaseDocuments(caseId: string): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/documents`);
  if (!res.ok) throw new Error('Failed to fetch case documents');
  return res.json();
}

export function getDocumentDownloadUrl(docId: string): string {
  return `${API_BASE}/documents/${docId}/download`;
}

export function getPageImageUrl(docId: string, pageNumber: number): string {
  return `${API_BASE}/documents/${docId}/pages/${pageNumber}/image`;
}

export async function triggerRun(caseId: string) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/runs`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to trigger investigation run');
  return res.json();
}

export async function fetchRun(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) throw new Error('Failed to fetch run details');
  return res.json();
}

export async function fetchRunFindings(runId: string): Promise<Finding[]> {
  const res = await fetch(`${API_BASE}/runs/${runId}/findings`);
  if (!res.ok) throw new Error('Failed to fetch findings');
  return res.json();
}

export async function fetchRunFields(runId: string): Promise<Field[]> {
  const res = await fetch(`${API_BASE}/runs/${runId}/fields`);
  if (!res.ok) throw new Error('Failed to fetch fields');
  return res.json();
}

export async function fetchRunClaims(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}/claims`);
  if (!res.ok) throw new Error('Failed to fetch claims');
  return res.json();
}

export async function fetchRunTransactions(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}/transactions`);
  if (!res.ok) throw new Error('Failed to fetch transactions');
  return res.json();
}

export async function fetchRunCoverage(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}/coverage`);
  if (!res.ok) throw new Error('Failed to fetch coverage matrix');
  return res.json();
}

export async function fetchRunGraph(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}/graph`);
  if (!res.ok) throw new Error('Failed to fetch claim graph');
  return res.json();
}

export async function generateRunReports(runId: string) {
  const res = await fetch(`${API_BASE}/runs/${runId}/reports`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate reports');
  return res.json();
}

export function getReportDownloadUrl(filename: string): string {
  return `${API_BASE}/reports/${filename}`;
}

export async function submitReview(findingId: string, data: { disposition: string; reason: string; actor_id?: string }) {
  const res = await fetch(`${API_BASE}/findings/${findingId}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to submit review');
  return res.json();
}

export async function submitFieldRevision(fieldId: string, data: { new_value: string; reason: string; expected_revision_num: number }) {
  const res = await fetch(`${API_BASE}/fields/${fieldId}/revisions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to submit revision');
  }
  return res.json();
}

export async function fetchCaseAudit(caseId: string): Promise<AuditEvent[]> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/audit`);
  if (!res.ok) throw new Error('Failed to fetch audit trail');
  return res.json();
}

export async function verifyCaseAudit(caseId: string) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/audit/verify`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to verify audit chain');
  return res.json();
}

export async function fetchCaseCheckpoint(caseId: string) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/checkpoint`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate checkpoint');
  return res.json();
}

export async function verifyRetainedCheckpoint(caseId: string, checkpointPayload: any) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/verify-checkpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(checkpointPayload),
  });
  if (!res.ok) throw new Error('Failed to verify checkpoint');
  return res.json();
}

export async function fetchCaseTimeline(caseId: string) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/timeline`);
  if (!res.ok) throw new Error('Failed to fetch case timeline');
  return res.json();
}
