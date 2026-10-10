// In production, when no external API URL is configured, serve an interactive
// browser-only demonstration. Local development continues to use the real FastAPI API.
export const BROWSER_DEMO = import.meta.env.PROD && !import.meta.env.VITE_API_BASE;
export const API_BASE = BROWSER_DEMO
  ? ''
  : (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000');

const DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST'];
const DEMO_PATTERNS = [
  { NORTH: 34, EAST: 12, SOUTH: 8, WEST: 15 },
  { NORTH: 22, EAST: 35, SOUTH: 12, WEST: 17 },
  { NORTH: 10, EAST: 42, SOUTH: 20, WEST: 30 },
  { NORTH: 18, EAST: 15, SOUTH: 32, WEST: 22 },
  { NORTH: 27, EAST: 19, SOUTH: 25, WEST: 11 },
];
const browserSession = {
  running: false,
  mode: 'IDLE',
  source: null,
  error: null,
  frames_processed: 0,
  started_at: null,
};

function densityFor(count) {
  if (count >= 40) return 'CRITICAL';
  if (count >= 25) return 'HIGH';
  if (count >= 12) return 'MEDIUM';
  return 'LOW';
}

function browserTrafficSnapshot() {
  const elapsed = Math.floor(Date.now() / 1000);
  const pattern = DEMO_PATTERNS[Math.floor(elapsed / 7) % DEMO_PATTERNS.length];
  const counts = Object.fromEntries(DIRECTIONS.map((direction) => {
    const pulse = Math.floor((elapsed % 11) / 4);
    return [direction, Math.max(0, pattern[direction] + ((pulse + DIRECTIONS.indexOf(direction)) % 3) - 1)];
  }));
  const phaseLength = 19;
  const phasePosition = elapsed % phaseLength;
  const phaseIndex = Math.floor(elapsed / phaseLength) % DIRECTIONS.length;
  const signalState = phasePosition < 15 ? 'GREEN' : phasePosition < 18 ? 'YELLOW' : 'ALL_RED';
  const remaining = phasePosition < 15
    ? 15 - phasePosition
    : phasePosition < 18 ? 18 - phasePosition : 19 - phasePosition;
  const activeDirection = DIRECTIONS[phaseIndex];
  const nextDirection = DIRECTIONS[(phaseIndex + 1) % DIRECTIONS.length];
  const lanes = DIRECTIONS.map((direction) => ({
    direction,
    vehicle_count: counts[direction],
    density: densityFor(counts[direction]),
    signal: signalState === 'ALL_RED' ? 'RED' : direction === activeDirection ? signalState : 'RED',
    remaining_seconds: direction === activeDirection ? remaining : 0,
  }));
  const total = lanes.reduce((sum, lane) => sum + lane.vehicle_count, 0);

  return {
    total_vehicles: total,
    vehicle_type_counts: {
      car: Math.round(total * 0.58),
      motorcycle: Math.round(total * 0.25),
      bus: Math.round(total * 0.07),
      truck: total - Math.round(total * 0.58) - Math.round(total * 0.25) - Math.round(total * 0.07),
    },
    active_direction: activeDirection,
    next_direction: nextDirection,
    signal_state: signalState,
    remaining_seconds: remaining,
    green_seconds: 15,
    signal_reason: 'Browser simulation: adaptive timing demonstration',
    emergency_detected: false,
    emergency_type: null,
    emergency_direction: null,
    emergency_confidence: 0,
    priority_active: false,
    lanes,
  };
}

function sampleHistory(limit = 20) {
  const now = Date.now();
  return Array.from({ length: Math.min(Math.max(Number(limit) || 20, 1), 60) }, (_, index) => {
    const age = (Math.min(Number(limit) || 20, 60) - index - 1) * 15000;
    const snapshot = browserTrafficSnapshotAt(now - age);
    return {
      recorded_at: new Date(now - age).toISOString(),
      total_vehicles: snapshot.total_vehicles,
      north: snapshot.lanes[0].vehicle_count,
      east: snapshot.lanes[1].vehicle_count,
      south: snapshot.lanes[2].vehicle_count,
      west: snapshot.lanes[3].vehicle_count,
      active_direction: snapshot.active_direction,
      signal_state: snapshot.signal_state,
    };
  });
}

function browserTrafficSnapshotAt(timestamp) {
  const elapsed = Math.floor(timestamp / 1000);
  const pattern = DEMO_PATTERNS[Math.floor(elapsed / 7) % DEMO_PATTERNS.length];
  const counts = Object.fromEntries(DIRECTIONS.map((direction) => [
    direction,
    Math.max(0, pattern[direction] + (Math.floor(elapsed / 4) + DIRECTIONS.indexOf(direction)) % 3 - 1),
  ]));
  const phasePosition = elapsed % 19;
  const phaseIndex = Math.floor(elapsed / 19) % DIRECTIONS.length;
  const signalState = phasePosition < 15 ? 'GREEN' : phasePosition < 18 ? 'YELLOW' : 'ALL_RED';
  const remaining = phasePosition < 15 ? 15 - phasePosition : phasePosition < 18 ? 18 - phasePosition : 19 - phasePosition;
  return {
    total_vehicles: Object.values(counts).reduce((sum, count) => sum + count, 0),
    active_direction: DIRECTIONS[phaseIndex],
    signal_state: signalState,
    remaining_seconds: remaining,
    lanes: DIRECTIONS.map((direction) => ({
      direction,
      vehicle_count: counts[direction],
    })),
  };
}

function browserSummary(limit = 100) {
  const history = sampleHistory(limit);
  const current = browserTrafficSnapshot();
  const average = (key) => history.length
    ? Math.round((history.reduce((sum, point) => sum + point[key], 0) / history.length) * 10) / 10
    : 0;
  const laneAverages = Object.fromEntries(['north', 'east', 'south', 'west'].map((lane) => [lane, average(lane)]));
  const busiestLane = Object.entries(laneAverages).sort((a, b) => b[1] - a[1])[0]?.[0] || 'north';
  const counts = {};
  history.forEach((point) => { counts[point.signal_state] = (counts[point.signal_state] || 0) + 1; });
  const values = history.map((point) => point.total_vehicles);
  return {
    data_points: history.length,
    average_vehicles: values.length ? Math.round(values.reduce((a, b) => a + b, 0) / values.length * 10) / 10 : 0,
    peak_vehicles: Math.max(current.total_vehicles, ...values, 0),
    minimum_vehicles: Math.min(...values, current.total_vehicles),
    current_vehicles: current.total_vehicles,
    busiest_lane: busiestLane.toUpperCase(),
    lane_averages: laneAverages,
    signal_state_counts: counts,
  };
}

async function getJson(path, options = {}) {
  if (BROWSER_DEMO) return browserDemoRequest(path, options);

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

function browserDemoRequest(path, options = {}) {
  const url = new URL(path, window.location.origin);
  const query = url.searchParams;
  if (url.pathname === '/api/system/status') {
    return Promise.resolve({ mode: 'browser-demo', ai_ready: false, database_ready: false, video_ready: true });
  }
  if (path === '/health') {
    return Promise.resolve({ status: 'ok', service: 'browser-traffic-demo', version: '1.0.0' });
  }
  if (url.pathname === '/api/system/diagnostics') {
    return Promise.resolve({
      healthy: true,
      checks: [
        { name: 'browser_simulation', ok: true, detail: 'Interactive traffic simulation is running entirely in this browser.' },
        { name: 'local_yolo_model', ok: false, detail: 'Real image-based AI inference is available in the local laptop version, not this hosted demo.' },
        { name: 'persistent_database', ok: false, detail: 'Hosted demo uses generated sample data; local SQLite persistence requires the backend.' },
        { name: 'video_input', ok: true, detail: 'Built-in animated intersection is available without uploading a video.' },
      ],
    });
  }
  if (url.pathname === '/api/traffic/snapshot') return Promise.resolve(browserTrafficSnapshot());
  if (url.pathname === '/api/video/sources') {
    return Promise.resolve([{
      path: 'browser-simulation',
      name: 'Browser Traffic Simulation',
      exists: true,
      readable: true,
      fps: 30,
      frame_count: 0,
      width: 1280,
      height: 720,
      duration_seconds: 0,
      error: null,
    }]);
  }
  if (url.pathname === '/api/video/session') {
    if (browserSession.running && browserSession.started_at) {
      browserSession.frames_processed = Math.floor((Date.now() - new Date(browserSession.started_at).getTime()) / 1000 * 12);
    }
    return Promise.resolve({ ...browserSession });
  }
  if (url.pathname === '/api/video/start' && options.method === 'POST') {
    let body = {};
    try { body = JSON.parse(options.body || '{}'); } catch (_) {}
    browserSession.running = true;
    browserSession.mode = 'SIMULATION_VIDEO';
    browserSession.source = body.path || 'browser-simulation';
    browserSession.error = null;
    browserSession.frames_processed = 0;
    browserSession.started_at = new Date().toISOString();
    return Promise.resolve({ ...browserSession });
  }
  if (url.pathname === '/api/video/stop' && options.method === 'POST') {
    browserSession.running = false;
    browserSession.mode = 'IDLE';
    browserSession.frames_processed = browserSession.frames_processed || 0;
    return Promise.resolve({ ...browserSession });
  }
  if (url.pathname === '/api/analytics/summary') {
    return Promise.resolve(browserSummary(Number(query.get('limit') || 100)));
  }
  if (url.pathname === '/api/analytics/history') {
    return Promise.resolve(sampleHistory(Number(query.get('limit') || 20)));
  }
  if (url.pathname === '/api/analytics/predict') {
    const horizon = Math.min(Math.max(Number(query.get('horizon') || 5), 1), 60);
    const current = browserTrafficSnapshot().total_vehicles;
    return Promise.resolve({
      data_points: Math.min(Number(query.get('limit') || 100), 60),
      predictions: Array.from({ length: Math.min(horizon, 5) }, (_, index) => ({
        horizon_minutes: index + 1,
        predicted_total_vehicles: Math.max(0, Math.round(current + Math.sin((Date.now() / 10000) + index) * (index + 2))),
        confidence: index < 2 ? 'MEDIUM' : 'LOW',
        method: 'Browser-demo trend simulation',
      })),
    });
  }
  if (url.pathname === '/api/video/status') {
    return Promise.resolve({
      path: query.get('path') || 'browser-simulation',
      exists: true,
      readable: true,
      fps: 30,
      frame_count: 0,
      width: 1280,
      height: 720,
      duration_seconds: 0,
      error: null,
    });
  }
  return Promise.reject(new Error('This endpoint is not available in browser demo mode.'));
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
