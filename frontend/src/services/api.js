export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

async function getJson(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), options.timeout ?? 5000);
  try {
    const response = await fetch(API_BASE + path, {
      ...options,
      signal: controller.signal,
    });
    if (!response.ok) {
      let detail = 'Backend returned ' + response.status;
      try {
        const body = await response.json();
        detail = body.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }
    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Backend request timed out');
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
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

export async function getVideoSources() {
  return getJson('/api/video/sources');
}

export async function getVideoSession() {
  return getJson('/api/video/session');
}

export async function startVideo(path, useAi = true) {
  return getJson('/api/video/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: path || null, use_ai: useAi }),
  });
}

export async function stopVideo() {
  return getJson('/api/video/stop', { method: 'POST' });
}

export async function getAnalyticsSummary(limit = 100) {
  return getJson('/api/analytics/summary?limit=' + limit);
}

export async function getAnalyticsHistory(limit = 20) {
  return getJson('/api/analytics/history?limit=' + limit);
}

export async function getAnalyticsPrediction(horizon = 5, limit = 100) {
  return getJson('/api/analytics/predict?horizon=' + horizon + '&limit=' + limit);
}

export async function getSystemDiagnostics() {
  return getJson('/api/system/diagnostics');
}
