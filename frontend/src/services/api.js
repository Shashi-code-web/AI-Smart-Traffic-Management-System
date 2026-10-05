export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

async function getJson(path, options) {
  const response = await fetch(API_BASE + path, options);
  if (!response.ok) {
    let detail = 'Backend returned ' + response.status;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
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

export async function getVideoSession() {
  return getJson('/api/video/session');
}

export async function startVideo(useAi = true) {
  return getJson('/api/video/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ use_ai: useAi }),
  });
}

export async function stopVideo() {
  return getJson('/api/video/stop', { method: 'POST' });
}
