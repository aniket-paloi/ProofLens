import { Case, Field, Finding, AuditEvent } from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch('/health/ready');
  return res.json();
}

export async function fetchCapabilities() {
  const res = await fetch('/capabilities');
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
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create case');
  }
  return res.json();
}

export async function fetchCase(caseId: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) throw new Error('Failed to fetch case details');
  return res.json();
}

export async function triggerRun(caseId: string) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/runs`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to trigger run');
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
    const err = await res.json();
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

