const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

async function getJson(path) {
  const response = await fetch(API_BASE + path);
  if (!response.ok) throw new Error('Backend returned ' + response.status);
  return response.json();
}

export async function getSystemStatus() {
  return getJson('/api/system/status');
}

export async function getHealth() {
  return getJson('/health');
}

export async function getTrafficSnapshot() {
  return getJson('/api/traffic/snapshot');
}

export async function getVideoStatus(path) {
  const query = path ? '?path=' + encodeURIComponent(path) : '';
  return getJson('/api/video/status' + query);
}
