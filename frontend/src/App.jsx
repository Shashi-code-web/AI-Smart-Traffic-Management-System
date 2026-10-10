import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity, BarChart3, Car, Gauge, Play, Radio, RefreshCw, Settings, ShieldAlert,
  Signal, Square, TrendingUp, Video, Wifi, WifiOff,
} from 'lucide-react';
import {
  API_BASE, BROWSER_DEMO, getAnalyticsHistory, getAnalyticsPrediction, getAnalyticsSummary,
  getHealth, getSystemDiagnostics, getSystemStatus, getTrafficSnapshot,
  getVideoSession, getVideoSources, startVideo, stopVideo,
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

function ConnectionBadge({ connected, checking, browserDemo }) {
  if (checking) return <div className="status"><span className="dot muted" /> Preparing dashboard…</div>;
  if (browserDemo) return <div className="status status-online"><Activity size={13} /> Browser demo ready</div>;
  return <div className={'status ' + (connected ? 'status-online' : 'status-offline')}>
    {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
    {connected ? 'Backend connected' : 'Backend offline'}
  </div>;
}

function BrowserIntersection({ traffic }) {
  const lanes = Object.fromEntries((traffic?.lanes || []).map((lane) => [lane.direction, lane]));
  const lane = (direction) => lanes[direction] || {};
  return <div className="browser-intersection" role="img" aria-label="Animated simulated four-way road intersection with traffic from all four directions">
    <div className="road road-horizontal" /><div className="road road-vertical" />
    <div className="road-markings markings-horizontal" /><div className="road-markings markings-vertical" />
    <div className="crosswalk crosswalk-top" /><div className="crosswalk crosswalk-bottom" />
    <div className="crosswalk crosswalk-left" /><div className="crosswalk crosswalk-right" />
    <div className="junction-center"><span>AI<br />NODE</span></div>
    {['NORTH','EAST','SOUTH','WEST'].map((direction) => <div key={direction} className={'junction-label junction-' + direction.toLowerCase()}>
      <strong>{direction}</strong><span>{lane(direction).vehicle_count ?? 0} vehicles</span>
      <i className={'mini-light ' + (lane(direction).signal || 'red').toLowerCase()} />
    </div>)}
    <span className="demo-car car-north-one" /><span className="demo-car car-north-two" />
    <span className="demo-car car-south-one" /><span className="demo-car car-east-one" />
    <span className="demo-car car-east-two" /><span className="demo-car car-west-one" />
    <div className="simulation-chip"><span className="dot" /> SIMULATED LIVE TRAFFIC</div>
  </div>;
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [video, setVideo] = useState(null);
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [analyticsSummary, setAnalyticsSummary] = useState(null);
  const [analyticsHistory, setAnalyticsHistory] = useState([]);
  const [analyticsPrediction, setAnalyticsPrediction] = useState(null);
  const [diagnostics, setDiagnostics] = useState(null);
  const [view, setView] = useState('overview');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [checking, setChecking] = useState(true);
  const [streamKey, setStreamKey] = useState(Date.now());

  const load = useCallback(async (includeSources = false) => {
    try {
      const [system, healthState, snapshot, session] = await Promise.all([
        getSystemStatus(),
        getHealth(),
        getTrafficSnapshot(),
        getVideoSession(),
      ]);
      const localSources = includeSources ? await getVideoSources() : [];
      const diagnosticsState = includeSources && view === 'settings'
        ? await getSystemDiagnostics()
        : null;

      if (view === 'analytics') {
        const [summaryState, historyState, predictionState] = await Promise.all([
          getAnalyticsSummary(100),
          getAnalyticsHistory(20),
          getAnalyticsPrediction(5, 100),
        ]);
        setAnalyticsSummary(summaryState);
        setAnalyticsHistory(historyState);
        setAnalyticsPrediction(predictionState);
      }

      setStatus(system);
      setHealth(healthState);
      setTraffic(snapshot);
      setVideo(session);
      if (includeSources) setSources(localSources);
      if (includeSources && view === 'settings') setDiagnostics(diagnosticsState);
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
  }, [selectedSource, view]);

  useEffect(() => {
    load(true);
    const timer = window.setInterval(() => load(false), 1500);
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
      await load(false);
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
      await load(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const refresh = async () => {
    setBusy(true);
    try {
      await load(true);
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
            <ConnectionBadge connected={Boolean(health?.status === 'ok')} checking={checking} browserDemo={BROWSER_DEMO} />
            <button className="icon-button" onClick={refresh} disabled={busy} title="Refresh data">
              <RefreshCw size={15} className={busy ? 'spin' : ''} />
            </button>
          </div>
        </header>

        {BROWSER_DEMO && <div className="demo-mode-banner" role="note">
          <div className="demo-mode-mark"><Activity size={17} /></div>
          <div><strong>Public interactive demo · simulated traffic</strong>
            <span>This website runs without installation. Counts, signal phases and forecasts are generated demo data, not live CCTV or real YOLO inference. The full AI video pipeline runs in the local laptop version.</span>
          </div>
        </div>}
        {error && <div className="error-banner" role="alert">{error}</div>

        {view === 'settings' ? (
          <section className="analytics-layout">
            <div className="metrics">
              <Metric
                icon={Wifi}
                label="Backend"
                value={BROWSER_DEMO ? 'DEMO' : health?.status === 'ok' ? 'ONLINE' : 'OFFLINE'}
                note={BROWSER_DEMO ? 'No backend required' : health?.version ? 'API v' + health.version : 'Health endpoint'}
              />
              <Metric
                icon={Car}
                label="AI model"
                value={status?.ai_ready ? 'READY' : 'SIMULATION'}
                note={status?.ai_ready ? 'Local YOLO available' : 'Offline fallback available'}
              />
              <Metric
                icon={Radio}
                label="Database"
                value={BROWSER_DEMO ? 'N/A' : status?.database_ready ? 'READY' : 'ERROR'}
                note={BROWSER_DEMO ? 'No hosted database' : 'SQLite local persistence'}
              />
              <Metric
                icon={Video}
                label="Video sources"
                value={sources.length}
                note={BROWSER_DEMO ? 'Built-in browser simulator' : 'Readable local sources'}
              />
            </div>

            <div className="grid-main">
              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>System Diagnostics</h2>
                    <p>Phase 8 reliability checks</p>
                  </div>
                  <span className="live-tag">
                    {diagnostics?.healthy ? 'HEALTHY' : 'CHECK REQUIRED'}
                  </span>
                </div>
                <div className="diagnostic-list">
                  {(diagnostics?.checks || []).map((check) => (
                    <div className="diagnostic-row" key={check.name}>
                      <span className={'diagnostic-dot ' + (check.ok ? 'ok' : 'bad')} />
                      <div>
                        <strong>{titleCase(check.name.replaceAll('_', ' '))}</strong>
                        <small>{check.detail}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>Offline Demo Workflow</h2>
                    <p>Designed for a 3–5 minute presentation</p>
                  </div>
                </div>
                <div className="demo-steps">
                  {BROWSER_DEMO ? <>
                    <div><b>01</b><span>Review lane counts and adaptive signal phases.</span></div>
                    <div><b>02</b><span>Open Live Monitor and start the animated browser simulation.</span></div>
                    <div><b>03</b><span>Compare lane density, signal states and countdowns.</span></div>
                    <div><b>04</b><span>Explore traffic history and the sample five-minute forecast.</span></div>
                    <div><b>05</b><span>Use this as a public UI demo; demonstrate real YOLO processing locally.</span></div>
                  </> : <>
                    <div><b>01</b><span>Open Overview and verify backend + database.</span></div>
                    <div><b>02</b><span>Select one of the local traffic videos.</span></div>
                    <div><b>03</b><span>Start AI Video; use simulation mode when no local YOLO model is installed.</span></div>
                    <div><b>04</b><span>Show signal phase, lane density, analytics, then Emergency view.</span></div>
                    <div><b>05</b><span>Finish by showing Diagnostics and final system status.</span></div>
                  </>}
                </div>
              </div>
            </div>
          </section>
        ) : view === 'emergency' ? (
          <section className="analytics-layout">
            <div className="metrics">
              <Metric
                icon={ShieldAlert}
                label="Emergency status"
                value={traffic?.emergency_detected ? 'DETECTED' : 'CLEAR'}
                note={traffic?.emergency_detected ? 'Local YOLO emergency class' : 'No emergency detected'}
              />
              <Metric
                icon={Car}
                label="Emergency type"
                value={traffic?.emergency_type?.replaceAll('_', ' ') || '—'}
                note={traffic?.emergency_confidence
                  ? Math.round(traffic.emergency_confidence * 100) + '% confidence'
                  : 'Waiting for detection'}
              />
              <Metric
                icon={Signal}
                label="Priority direction"
                value={titleCase(traffic?.emergency_direction || '—')}
                note={traffic?.priority_active ? 'Signal preemption active' : 'No priority request'}
              />
              <Metric
                icon={Radio}
                label="Signal state"
                value={traffic?.signal_state || 'GREEN'}
                note={traffic?.signal_reason || 'Normal adaptive control'}
              />
            </div>

            <div className="grid-main">
              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>Emergency Priority</h2>
                    <p>Safe preemption through the Phase 5 signal controller</p>
                  </div>
                  <span className="live-tag">
                    <span className="dot" /> {traffic?.priority_active ? 'PRIORITY ACTIVE' : 'STANDBY'}
                  </span>
                </div>
                <div className="emergency-banner-panel">
                  <ShieldAlert size={36} />
                  <div>
                    <strong>
                      {traffic?.emergency_detected
                        ? titleCase(traffic.emergency_type || 'emergency vehicle') + ' detected'
                        : 'No emergency vehicle detected'}
                    </strong>
                    <span>{traffic?.emergency_detected
                      ? 'Direction: ' + titleCase(traffic.emergency_direction || 'unmapped') + '. The controller uses yellow and all-red clearance before priority green.'
                      : BROWSER_DEMO
                        ? 'This public browser demo does not run image-based emergency recognition. The local version can detect supported classes with a compatible trained YOLO model.'
                        : 'Emergency recognition requires a local YOLO model trained with supported ambulance, fire-truck, police, or emergency-vehicle classes.'}</span>
                  </div>
                </div>
              </div>

              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>Supported emergency classes</h2>
                    <p>Detected from local YOLO class labels</p>
                  </div>
                </div>
                <div className="lane-average-grid">
                  {['AMBULANCE', 'FIRE TRUCK', 'POLICE', 'EMERGENCY VEHICLE'].map((label) => (
                    <div className="lane-average" key={label}>
                      <span>{label}</span>
                      <strong>SUPPORTED</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        ) : view === 'analytics' ? (
          <section className="analytics-layout">
            <div className="metrics">
              <Metric
                icon={BarChart3}
                label="Data points"
                value={analyticsSummary?.data_points ?? '—'}
                note="Persisted local samples"
              />
              <Metric
                icon={Gauge}
                label="Average vehicles"
                value={analyticsSummary?.average_vehicles ?? '—'}
                note="Selected history window"
              />
              <Metric
                icon={Car}
                label="Peak vehicles"
                value={analyticsSummary?.peak_vehicles ?? '—'}
                note="Highest recorded load"
              />
              <Metric
                icon={TrendingUp}
                label="5-min forecast"
                value={analyticsPrediction?.predictions?.[4]?.predicted_total_vehicles ?? '—'}
                note={analyticsPrediction?.predictions?.[4]?.confidence
                  ? analyticsPrediction.predictions[4].confidence + ' confidence'
                  : 'Building forecast'}
              />
            </div>

            <div className="grid-main">
              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>Traffic History</h2>
                    <p>Latest persisted traffic samples</p>
                  </div>
                  <span className="live-tag">{analyticsSummary?.busiest_lane || '—'} busiest</span>
                </div>
                <div className="lane-table">
                  <div className="lane-row lane-header">
                    <span>Time</span><span>Total</span><span>North</span><span>East</span><span>Signal</span>
                  </div>
                  {analyticsHistory.length ? analyticsHistory.slice().reverse().map((point) => (
                    <div className="lane-row" key={point.recorded_at + point.total_vehicles}>
                      <span>{new Date(point.recorded_at).toLocaleTimeString()}</span>
                      <strong>{point.total_vehicles}</strong>
                      <span>{point.north}</span>
                      <span>{point.east}</span>
                      <span>{point.signal_state}</span>
                    </div>
                  )) : (
                    <div className="analytics-empty">
                      Traffic history will populate automatically while the dashboard is running.
                    </div>
                  )}
                </div>
              </div>

              <div className="card analytics-card">
                <div className="section-head">
                  <div>
                    <h2>Traffic Forecast</h2>
                    <p>Short-term offline trend prediction</p>
                  </div>
                </div>
                <div className="forecast-list">
                  {(analyticsPrediction?.predictions || []).map((prediction) => (
                    <div className="forecast-row" key={prediction.horizon_minutes}>
                      <span>+{prediction.horizon_minutes} min</span>
                      <strong>{prediction.predicted_total_vehicles}</strong>
                      <small>{prediction.confidence}</small>
                    </div>
                  ))}
                  {!analyticsPrediction?.predictions?.length && (
                    <div className="analytics-empty">
                      At least two historical samples are needed to forecast a trend.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="card analytics-card">
              <div className="section-head">
                <div>
                  <h2>Lane Averages</h2>
                  <p>Average vehicles per persisted sample</p>
                </div>
                <span className="live-tag">Current {analyticsSummary?.current_vehicles ?? '—'}</span>
              </div>
              <div className="lane-average-grid">
                {Object.entries(analyticsSummary?.lane_averages || {}).map(([lane, value]) => (
                  <div className="lane-average" key={lane}>
                    <span>{titleCase(lane)}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>
        ) : view !== 'overview' ? (
          <div className="card info-panel">
            <strong>{titleCase(view)} module</strong>
            <span>
              {BROWSER_DEMO
                ? 'This public website demonstrates the dashboard interface and simulated traffic states without requiring a local backend.'
                : 'This dashboard is connected to the live backend. Advanced ' + view + ' intelligence is implemented in its later project phase.'}
            </span>
          </div>
        ) : null}

        <section className="metrics">
          <Metric icon={Car} label={BROWSER_DEMO ? 'Vehicles in simulation' : 'Vehicles detected'} value={traffic?.total_vehicles ?? '—'} note={BROWSER_DEMO ? 'Generated sample traffic' : video?.running ? 'Live AI snapshot' : 'Current traffic snapshot'} />
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
                <p>{BROWSER_DEMO ? (video?.running ? 'Browser simulation running' : 'Interactive browser simulator') : sessionLabel}</p>
              </div>
              <span className="live-tag">
                <span className="dot" /> {video?.running ? 'LIVE' : (video?.mode === 'AI_VIDEO' ? 'DONE' : 'READY')}
              </span>
            </div>

            {BROWSER_DEMO && video?.running ? <BrowserIntersection traffic={traffic} />
              : !BROWSER_DEMO && (video?.running || video?.mode === 'AI_VIDEO') ? (
                <img key={streamKey} className="video-stream" src={streamUrl} alt="Live traffic detection stream" onError={() => {}} />
              ) : <div className="video-placeholder">
                <Video size={34} />
                <strong>{BROWSER_DEMO ? 'Start the browser traffic simulation' : sources.length ? 'Select a traffic video' : 'Add a local traffic video'}</strong>
                <span>{BROWSER_DEMO
                  ? 'The animated intersection uses generated traffic data so your professor can explore the dashboard in any browser.'
                  : <>Videos must be stored under <code>data/videos/</code>. Phase 7 can use any readable MP4/AVI/MOV/MKV/M4V file.</>}</span>
              </div>}

            <div className="video-controls">
              <div className="source-picker">
                <label htmlFor="video-source">{BROWSER_DEMO ? 'Simulation source' : 'Video source'}</label>
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
                <p>Phase 5 safety state machine + Phase 7 emergency priority</p>
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
            <div><h2>Lane Conditions</h2><p>{BROWSER_DEMO ? 'Browser-generated simulation updates every 1.5 seconds' : 'Updated from the backend every 1.5 seconds'}</p></div>
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
