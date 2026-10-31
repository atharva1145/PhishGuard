import {
  HealthData,
  UrlScanResult,
  EmailScanResult,
  AllMetricsData,
  HistoryItem,
  DefangResponse,
  CounterfactualResult,
  BatchUrlScanResult
} from '../types';

const API_BASE = '/api';

export async function checkHealth(): Promise<HealthData> {
  const resp = await fetch(`${API_BASE}/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function scanUrl(url: string): Promise<UrlScanResult> {
  const resp = await fetch(`${API_BASE}/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url.trim() }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `URL scan failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function scanEmail(subject: string, body: string): Promise<EmailScanResult> {
  const resp = await fetch(`${API_BASE}/scan/email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject: subject.trim(), body: body.trim() }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Email scan failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function scanEmailFile(file: File): Promise<EmailScanResult> {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch(`${API_BASE}/scan/email/file`, {
    method: 'POST',
    body: formData,
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Email file upload failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function getMetrics(): Promise<AllMetricsData> {
  const resp = await fetch(`${API_BASE}/metrics`);
  if (!resp.ok) {
    throw new Error(`Failed to load metrics with status ${resp.status}`);
  }
  return resp.json();
}

export async function getHistory(params?: {
  scan_type?: string;
  prediction?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: HistoryItem[] }> {
  const query = new URLSearchParams();
  if (params?.scan_type && params.scan_type !== 'all') query.append('scan_type', params.scan_type);
  if (params?.prediction && params.prediction !== 'all') query.append('prediction', params.prediction);
  if (params?.search) query.append('search', params.search);
  if (params?.limit) query.append('limit', params.limit.toString());
  if (params?.offset) query.append('offset', params.offset.toString());

  const resp = await fetch(`${API_BASE}/history?${query.toString()}`);
  if (!resp.ok) {
    throw new Error(`Failed to load history with status ${resp.status}`);
  }
  return resp.json();
}

export async function deleteHistoryItem(scanId: string): Promise<{ success: boolean; message: string }> {
  const resp = await fetch(`${API_BASE}/history/${scanId}`, {
    method: 'DELETE',
  });
  if (!resp.ok) {
    throw new Error(`Failed to delete record: status ${resp.status}`);
  }
  return resp.json();
}

export async function clearAllHistory(): Promise<{ success: boolean; message: string }> {
  const resp = await fetch(`${API_BASE}/history`, {
    method: 'DELETE',
  });
  if (!resp.ok) {
    throw new Error(`Failed to clear history: status ${resp.status}`);
  }
  return resp.json();
}

export async function defangIndicator(url: string, action: 'defang' | 'refang' = 'defang'): Promise<DefangResponse> {
  const resp = await fetch(`${API_BASE}/defang`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url.trim(), action }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Defang request failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function simulateCounterfactual(
  url: string,
  modifications: Record<string, boolean>
): Promise<CounterfactualResult> {
  const resp = await fetch(`${API_BASE}/scan/url/counterfactual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url.trim(), modifications }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Counterfactual simulation failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function scanUrlBatch(urls: string[]): Promise<BatchUrlScanResult> {
  const resp = await fetch(`${API_BASE}/scan/url/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Batch scan failed with status ${resp.status}`);
  }
  return resp.json();
}
