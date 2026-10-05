import { useEffect, useMemo, useState } from 'react';
import { Activity, Car, Gauge, Radio, Settings, ShieldAlert, Signal, Video } from 'lucide-react';
import { getSystemStatus, getTrafficSnapshot } from './services/api';

function titleCase(value) {
  return value.charAt(0) + value.slice(1).toLowerCase();
}

function Metric({ icon: Icon, label, value, note }) {
  return <div className="metric card"><div className="metric-icon"><Icon size={19}/></div><div><p>{label}</p><strong>{value}</strong><span>{note}</span></div></div>;
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const [system, snapshot] = await Promise.all([getSystemStatus(), getTrafficSnapshot()]);
        if (!mounted) return;
        setStatus(system);
        setTraffic(snapshot);
        setError('');
      } catch (err) {
        if (mounted) setError(err.message);
      }
    };
    load();
    const timer = window.setInterval(load, 1000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, []);

  const overallDensity = useMemo(() => {
    const priority = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    return priority.find((level) => traffic?.lanes?.some((lane) => lane.density === level)) || 'LOW';
  }, [traffic]);

  const activeDirection = traffic?.active_direction || 'NORTH';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Signal size={22}/></div><div><strong>Traffic AI</strong><span>Control Center</span></div></div>
        <nav><a className="active"><Activity size={18}/>Overview</a><a><Video size={18}/>Live Monitor</a><a><Gauge size={18}/>Analytics</a><a><ShieldAlert size={18}/>Emergency</a><a><Settings size={18}/>Settings</a></nav>
        <div className="system-pill"><span className="dot"/>Offline-ready demo</div>
      </aside>

      <main className="main">
        <header className="topbar"><div><p className="eyebrow">AI SMART TRAFFIC MANAGEMENT</p><h1>Intersection Overview</h1></div><div className="status"><span className="dot"/>System {status?.mode === 'demo' ? 'Demo' : 'Connecting'}</div></header>

        {error && <div className="error-banner">Backend unavailable: {error}. Start the FastAPI server to enable live status.</div>}

        <section className="metrics">
          <Metric icon={Car} label="Vehicles detected" value={traffic?.total_vehicles ?? '—'} note="Live traffic snapshot" />
          <Metric icon={Gauge} label="Traffic density" value={overallDensity} note="Highest active lane demand" />
          <Metric icon={Signal} label="Active signal" value={titleCase(activeDirection)} note={'Green · ' + (traffic?.remaining_seconds ?? '—') + ' sec'} />
          <Metric icon={Radio} label="System mode" value={(status?.mode || 'demo').toUpperCase()} note={status?.ai_ready ? 'Local YOLO ready' : 'Offline simulation active'} />
        </section>

        <section className="grid-main">
          <div className="card video-card"><div className="section-head"><div><h2>AI Traffic Monitor</h2><p>Offline demo state is live; video ingestion follows the same pipeline.</p></div><span className="live-tag"><span className="dot"/> {status?.ai_ready ? 'AI READY' : 'DEMO'}</span></div><div className="video-placeholder"><Video size={34}/><strong>{status?.video_ready ? 'Traffic video input ready' : 'Traffic video input not loaded'}</strong><span>Place the presentation video at <code>data/videos/demo.mp4</code> to validate it locally. Supply the model under <code>models/yolo/</code> for real YOLO + ByteTrack processing.</span><button>Start Demo</button></div></div>
          <div className="card signal-card"><div className="section-head"><div><h2>Signal Controller</h2><p>Adaptive offline simulation</p></div></div><div className="signal-lights"><div className="light red"/><div className="light yellow"/><div className="light green active"/></div><div className="signal-current"><span>{titleCase(activeDirection)} / Green</span><strong>{traffic?.remaining_seconds ?? '—'}s</strong></div><div className="safe-note">Conflict protection enabled</div></div>
        </section>

        <section className="card"><div className="section-head"><div><h2>Lane Conditions</h2><p>Current traffic state from the backend snapshot</p></div></div><div className="lane-table"><div className="lane-row lane-header"><span>Lane</span><span>Vehicles</span><span>Density</span><span>Signal</span><span>Remaining</span></div>{(traffic?.lanes || []).map((lane) => <div className="lane-row" key={lane.direction}><strong>{titleCase(lane.direction)}</strong><span>{lane.vehicle_count}</span><span className={'density ' + lane.density.toLowerCase()}>{lane.density}</span><span><i className={'mini-light ' + lane.signal.toLowerCase()}/>{lane.signal}</span><span>{lane.direction === activeDirection ? lane.remaining_seconds : 24}s</span></div>)}</div></section>
      </main>
    </div>
  );
}
