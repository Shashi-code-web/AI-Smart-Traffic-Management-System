const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

export async function getSystemStatus() {
  const response = await fetch(`${API_BASE}/api/system/status`);
  if (!response.ok) throw new Error(`Backend returned ${response.status}`);
  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error(`Backend returned ${response.status}`);
  return response.json();
}