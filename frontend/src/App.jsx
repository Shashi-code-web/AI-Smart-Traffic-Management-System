import { useEffect, useState } from 'react';
import { Activity, Car, Gauge, Radio, Settings, ShieldAlert, Signal, Video } from 'lucide-react';
import { getSystemStatus } from './services/api';

const lanes = [
  { name: 'North', density: 'MEDIUM', count: 18, state: 'RED', time: 24 },
  { name: 'South', density: 'LOW', count: 7, state: 'GREEN', time: 18 },
  { name: 'East', density: 'HIGH', count: 31, state: 'GREEN', time: 42 },
  { name: 'West', density: 'LOW', count: 11, state: 'RED', time: 24 },
];

function Metric({ icon: Icon, label, value, note }) {
  return <div className="metric card"><div className="metric-icon"><Icon size={19}/></div><div><p>{label}</p><strong>{value}</strong><span>{note}</span></div></div>;
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getSystemStatus().then(setStatus).catch((err) => setError(err.message));
  }, []);

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
          <Metric icon={Car} label="Vehicles detected" value="67" note="Live count placeholder" />
          <Metric icon={Gauge} label="Traffic density" value="HIGH" note="East lane priority" />
          <Metric icon={Signal} label="Active signal" value="EAST" note="Green · 42 sec" />
          <Metric icon={Radio} label="System mode" value="DEMO" note="Offline presentation ready" />
        </section>
        <section className="grid-main">
          <div className="card video-card"><div className="section-head"><div><h2>AI Traffic Monitor</h2><p>Phase 1 dashboard shell · AI video module coming next</p></div><span className="live-tag"><span className="dot"/> READY</span></div><div className="video-placeholder"><Video size={34}/><strong>Traffic video input</strong><span>Start Demo will connect this panel to the local OpenCV + YOLO pipeline.</span><button>Start Demo</button></div></div>
          <div className="card signal-card"><div className="section-head"><div><h2>Signal Controller</h2><p>Adaptive simulation</p></div></div><div className="signal-lights"><div className="light red"/><div className="light yellow"/><div className="light green active"/></div><div className="signal-current"><span>East / Green</span><strong>42s</strong></div><div className="safe-note">Conflict protection enabled</div></div>
        </section>
        <section className="card"><div className="section-head"><div><h2>Lane Conditions</h2><p>Current traffic state across the intersection</p></div></div><div className="lane-table"><div className="lane-row lane-header"><span>Lane</span><span>Vehicles</span><span>Density</span><span>Signal</span><span>Remaining</span></div>{lanes.map((lane) => <div className="lane-row" key={lane.name}><strong>{lane.name}</strong><span>{lane.count}</span><span className={`density ${lane.density.toLowerCase()}`}>{lane.density}</span><span><i className={`mini-light ${lane.state.toLowerCase()}`}/>{lane.state}</span><span>{lane.time}s</span></div>)}</div></section>
      </main>
    </div>
  );
}