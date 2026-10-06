import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity, Car, Gauge, Play, Radio, RefreshCw, Settings, ShieldAlert,
  Signal, Square, Video, Wifi, WifiOff,
} from 'lucide-react';
import {
  API_BASE, getHealth, getSystemStatus, getTrafficSnapshot, getVideoSession,
  getVideoSources, startVideo, stopVideo,
} from './services/api';

function titleCase(value = '') {
  return value ? value.charAt(0) + value.slice(1).toLowerCase() : '—';
}

function formatDuration(seconds = 0) {
  if (!seconds) return '0s';
  const minutes = Math.floor(seconds / 60);
  const remainder = Math.round(seconds % 60);
  return minutes ? `${minutes}m ${remainder}s` : `${remainder}s`;
}

function Metric({ icon: Icon, label, value, note }) {
  return (
    <div className="metric card">
      <div className="metric-icon"><Icon size={19} /></div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <span>{note}</span>
      </div>
    </div>
  );
}

function ConnectionBadge({ connected, checking }) {
  if (checking) {
    return <div className="status"><span className="dot muted" /> Checking backend…</div>;
  }
  return (
    <div className={'status ' + (connected ? 'status-online' : 'status-offline')}>
      {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
      {connected ? 'Backend connected' : 'Backend offline'}
    </div>
  );
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [video, setVideo] = useState(null);
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [view, setView] = useState('overview');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [checking, setChecking] = useState(true);
  const [streamKey, setStreamKey] = useState(Date.now());

  const load = useCallback(async () => {
    try {
      const [system, healthState, snapshot, session, localSources] = await Promise.all([
        getSystemStatus(),
        getHealth(),
        getTrafficSnapshot(),
        getVideoSession(),
        getVideoSources(),
      ]);

      setStatus(system);
      setHealth(healthState);
      setTraffic(snapshot);
      setVideo(session);
      setSources(localSources);
      setError('');
      setChecking(false);

      if (!selectedSource && localSources.length) {
        const preferred =
          localSources.find((source) => source.path === 'data/videos/demo.mp4') ||
          localSources[0];
        setSelectedSource(preferred.path);
      }
    } catch (err) {
      setChecking(false);
      setError(err.message);
    }
  }, [selectedSource]);

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 1500);
    return () => window.clearInterval(timer);
  }, [load]);

  const overallDensity = useMemo(() => {
    const priority = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    return priority.find((level) =>
      traffic?.lanes?.some((lane) => lane.density === level)
    ) || 'LOW';
  }, [traffic]);

  const activeDirection = traffic?.active_direction || 'NORTH';
  const selected = sources.find((source) => source.path === selectedSource);
  const aiMode = Boolean(status?.ai_ready);

  const runVideo = async () => {
    if (!selectedSource) {
      setError('Select a local traffic video first.');
      return;
    }
    setBusy(true);
    try {
      await startVideo(selectedSource, aiMode);
      setStreamKey(Date.now());
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const stop = async () => {
    setBusy(true);
    try {
      await stopVideo();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const refresh = async () => {
    setBusy(true);
    try {
      await load();
    } finally {
      setBusy(false);
    }
  };

  const streamUrl = API_BASE + '/api/video/stream?session=' + streamKey;
  const sessionLabel = video?.mode === 'AI_VIDEO'
    ? (video.running ? 'AI processing live' : 'AI video complete')
    : video?.mode === 'SIMULATION_VIDEO'
      ? (video.running ? 'Simulation live' : 'Simulation complete')
      : 'Ready for local video input';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Signal size={22} /></div>
          <div><strong>Traffic AI</strong><span>Control Center</span></div>
        </div>

        <nav>
          {[
            ['overview', Activity, 'Overview'],
            ['live', Video, 'Live Monitor'],
            ['analytics', Gauge, 'Analytics'],
            ['emergency', ShieldAlert, 'Emergency'],
            ['settings', Settings, 'Settings'],
          ].map(([key, Icon, label]) => (
            <button
              key={key}
              className={view === key ? 'nav-button active' : 'nav-button'}
              onClick={() => setView(key)}
            >
              <Icon size={18} />{label}
            </button>
          ))}
        </nav>

        <div className="system-pill">
          <span className="dot" />
          Offline-ready demo
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI SMART TRAFFIC MANAGEMENT</p>
            <h1>{view === 'overview' ? 'Intersection Overview' : titleCase(view)}</h1>
          </div>
          <div className="topbar-actions">
            <ConnectionBadge connected={Boolean(health?.status === 'ok')} checking={checking} />
            <button className="icon-button" onClick={refresh} disabled={busy} title="Refresh data">
              <RefreshCw size={15} className={busy ? 'spin' : ''} />
            </button>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        {view !== 'overview' && (
          <div className="card info-panel">
            <strong>{titleCase(view)} module</strong>
            <span>
              This dashboard is connected to the live backend. Advanced {view} intelligence is implemented in its later project phase.
            </span>
          </div>
        )}

        <section className="metrics">
          <Metric icon={Car} label="Vehicles detected" value={traffic?.total_vehicles ?? '—'} note={video?.running ? 'Live AI snapshot' : 'Current traffic snapshot'} />
          <Metric icon={Gauge} label="Traffic density" value={overallDensity} note="Highest lane demand" />
          <Metric
            icon={Signal}
            label="Signal phase"
            value={traffic?.signal_state || 'GREEN'}
            note={traffic?.signal_state === 'ALL_RED'
              ? 'Safety clearance'
              : `${titleCase(activeDirection)} · ${traffic?.remaining_seconds ?? '—'} sec`}
/>
          <Metric icon={Radio} label="System mode" value={aiMode ? 'AI' : 'DEMO'} note={aiMode ? 'Local YOLO available' : 'Offline simulation'} />
        </section>

        <section className="grid-main">
          <div className="card video-card">
            <div className="section-head">
              <div>
                <h2>AI Traffic Monitor</h2>
                <p>{sessionLabel}</p>
              </div>
              <span className="live-tag">
                <span className="dot" /> {video?.running ? 'LIVE' : (video?.mode === 'AI_VIDEO' ? 'DONE' : 'READY')}
              </span>
            </div>

            {video?.running || video?.mode === 'AI_VIDEO' ? (
              <img
                key={streamKey}
                className="video-stream"
                src={streamUrl}
                alt="Live traffic detection stream"
                onError={() => {}}
              />
            ) : (
              <div className="video-placeholder">
                <Video size={34} />
                <strong>{sources.length ? 'Select a traffic video' : 'Add a local traffic video'}</strong>
                <span>
                  Videos must be stored under <code>data/videos/</code>.
                  Phase 4 can use any readable MP4/AVI/MOV/MKV/M4V file.
                </span>
              </div>
            )}

            <div className="video-controls">
              <div className="source-picker">
                <label htmlFor="video-source">Video source</label>
                <select
                  id="video-source"
                  value={selectedSource}
                  onChange={(event) => setSelectedSource(event.target.value)}
                  disabled={video?.running || busy || !sources.length}
                >
                  {!sources.length && <option value="">No local videos found</option>}
                  {sources.map((source) => (
                    <option key={source.path} value={source.path}>
                      {source.name} · {formatDuration(source.duration_seconds)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="source-meta">
                {selected ? (
                  <>
                    <span>{selected.width}×{selected.height}</span>
                    <span>{selected.fps.toFixed(1)} FPS</span>
                    <span>{selected.readable ? 'Readable' : 'Unavailable'}</span>
                  </>
                ) : <span>No source selected</span>}
              </div>

              <div className="control-actions">
                {video?.running ? (
                  <button className="stop-button" onClick={stop} disabled={busy}>
                    <Square size={13} /> Stop
                  </button>
                ) : (
                  <button
                    className="primary-button"
                    onClick={runVideo}
                    disabled={busy || !selectedSource || !selected?.readable}
                  >
                    <Play size={14} /> {busy ? 'Starting…' : (aiMode ? 'Start AI Video' : 'Start Demo Video')}
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="card signal-card">
            <div className="section-head">
              <div>
                <h2>Signal Controller</h2>
                <p>Phase 5 adaptive safety state machine</p>
              </div>
            </div>
            <div className="signal-lights">
              <div className={'light red ' + (traffic?.signal_state === 'RED' || traffic?.signal_state === 'ALL_RED' ? 'active' : '')} />
              <div className={'light yellow ' + (traffic?.signal_state === 'YELLOW' ? 'active' : '')} />
              <div className={'light green ' + (traffic?.signal_state === 'GREEN' ? 'active' : '')} />
            </div>
            <div className="signal-current">
              <span>
                {traffic?.signal_state === 'ALL_RED'
                  ? 'All directions / Safety clearance'
                  : titleCase(activeDirection) + ' / ' + (traffic?.signal_state || 'GREEN')}
              </span>
              <strong>{traffic?.remaining_seconds ?? '—'}s</strong>
            </div>
            <div className="safe-note">
              Next: {titleCase(traffic?.next_direction || activeDirection)}
            </div>
          </div>
        </section>

        <section className="card">
          <div className="section-head">
            <div><h2>Lane Conditions</h2><p>Updated from the backend every 1.5 seconds</p></div>
          </div>
          <div className="lane-table">
            <div className="lane-row lane-header">
              <span>Lane</span><span>Vehicles</span><span>Density</span><span>Signal</span><span>Remaining</span>
            </div>
            {(traffic?.lanes || []).map((lane) => (
              <div className="lane-row" key={lane.direction}>
                <strong>{titleCase(lane.direction)}</strong>
                <span>{lane.vehicle_count}</span>
                <span className={'density ' + lane.density.toLowerCase()}>{lane.density}</span>
                <span><i className={'mini-light ' + lane.signal.toLowerCase()} />{lane.signal}</span>
                <span>{lane.direction === activeDirection ? lane.remaining_seconds : '—'}s</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
