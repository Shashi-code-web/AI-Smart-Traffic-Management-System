import { useEffect, useMemo, useState } from 'react';
import { Activity, Car, Gauge, Radio, Settings, ShieldAlert, Signal, Square, Video } from 'lucide-react';
import { API_BASE, getSystemStatus, getTrafficSnapshot, getVideoSession, startVideo, stopVideo } from './services/api';

function titleCase(value) {
  return value.charAt(0) + value.slice(1).toLowerCase();
}

function Metric({ icon: Icon, label, value, note }) {
  return <div className="metric card"><div className="metric-icon"><Icon size={19}/></div><div><p>{label}</p><strong>{value}</strong><span>{note}</span></div></div>;
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [video, setVideo] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    try {
      const [system, snapshot, session] = await Promise.all([getSystemStatus(), getTrafficSnapshot(), getVideoSession()]);
      setStatus(system);
      setTraffic(snapshot);
      setVideo(session);
      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const overallDensity = useMemo(() => {
    const priority = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    return priority.find((level) => traffic?.lanes?.some((lane) => lane.density === level)) || 'LOW';
  }, [traffic]);

  const activeDirection = traffic?.active_direction || 'NORTH';

  const runVideo = async () => {
    setBusy(true);
    try {
      await startVideo(Boolean(status?.ai_ready));
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

  const streamUrl = API_BASE + '/api/video/stream';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Signal size={22}/></div><div><strong>Traffic AI</strong><span>Control Center</span></div></div>
        <nav><a className="active"><Activity size={18}/>Overview</a><a><Video size={18}/>Live Monitor</a><a><Gauge size={18}/>Analytics</a><a><ShieldAlert size={18}/>Emergency</a><a><Settings size={18}/>Settings</a></nav>
        <div className="system-pill"><span className="dot"/>Offline-ready demo</div>
      </aside>

      <main className="main">
        <header className="topbar"><div><p className="eyebrow">AI SMART TRAFFIC MANAGEMENT</p><h1>Intersection Overview</h1></div><div className="status"><span className="dot"/>System {status?.mode === 'demo' ? 'Demo' : 'Connecting'}</div></header>
        {error && <div className="error-banner">{error}</div>}

        <section className="metrics">
          <Metric icon={Car} label="Vehicles detected" value={traffic?.total_vehicles ?? '—'} note="Live traffic snapshot" />
          <Metric icon={Gauge} label="Traffic density" value={overallDensity} note="Highest lane demand" />
          <Metric icon={Signal} label="Active signal" value={titleCase(activeDirection)} note={'Green · ' + (traffic?.remaining_seconds ?? '—') + ' sec'} />
          <Metric icon={Radio} label="System mode" value={(status?.mode || 'demo').toUpperCase()} note={status?.ai_ready ? 'Local YOLO ready' : 'Offline simulation active'} />
        </section>

        <section className="grid-main">
          <div className="card video-card"><div className="section-head"><div><h2>AI Traffic Monitor</h2><p>{video?.running ? video.mode.replace('_', ' ') : 'Ready for local video input'}</p></div><span className="live-tag"><span className="dot"/> {video?.running ? 'LIVE' : (status?.ai_ready ? 'AI READY' : 'DEMO')}</span></div>
            {video?.running ? <img className="video-stream" src={streamUrl} alt="Live traffic detection stream" /> : <div className="video-placeholder"><Video size={34}/><strong>{status?.video_ready ? 'Traffic video input ready' : 'Add a local demo video'}</strong><span>Place the presentation video at <code>data/videos/demo.mp4</code>. Add a local YOLO weight under <code>models/yolo/</code> for real AI tracking.</span><button onClick={runVideo} disabled={busy || !status?.video_ready}>{busy ? 'Starting…' : (status?.ai_ready ? 'Start AI Video' : 'Start Simulation Video')}</button></div>}
          </div>
          <div className="card signal-card"><div className="section-head"><div><h2>Signal Controller</h2><p>Adaptive offline simulation</p></div></div><div className="signal-lights"><div className="light red"/><div className="light yellow"/><div className="light green active"/></div><div className="signal-current"><span>{titleCase(activeDirection)} / Green</span><strong>{traffic?.remaining_seconds ?? '—'}s</strong></div><div className="safe-note">Conflict protection enabled</div>{video?.running && <button className="stop-button" onClick={stop} disabled={busy}><Square size={13}/> Stop video</button>}</div>
        </section>

        <section className="card"><div className="section-head"><div><h2>Lane Conditions</h2><p>Current traffic state from the backend</p></div></div><div className="lane-table"><div className="lane-row lane-header"><span>Lane</span><span>Vehicles</span><span>Density</span><span>Signal</span><span>Remaining</span></div>{(traffic?.lanes || []).map((lane) => <div className="lane-row" key={lane.direction}><strong>{titleCase(lane.direction)}</strong><span>{lane.vehicle_count}</span><span className={'density ' + lane.density.toLowerCase()}>{lane.density}</span><span><i className={'mini-light ' + lane.signal.toLowerCase()}/>{lane.signal}</span><span>{lane.direction === activeDirection ? lane.remaining_seconds : 24}s</span></div>)}</div></section>
      </main>
    </div>
  );
}
