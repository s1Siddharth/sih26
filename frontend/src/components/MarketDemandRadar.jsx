import React, { useEffect, useMemo, useState } from 'react';
import { fetchDemand } from '../api/client';

const SECTORS = ['All', 'IT / Digital', 'Manufacturing', 'Automotive / EV', 'Healthcare', 'Logistics', 'Renewable Energy'];

export default function MarketDemandRadar() {
  const [sector, setSector] = useState('All');
  const [role, setRole] = useState('All');
  const [location, setLocation] = useState('All');
  const [level, setLevel] = useState('All');
  const [data, setData] = useState({ signals: [], summary: {}, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    fetchDemand({
      sector: sector === 'All' ? undefined : sector,
      role: role === 'All' ? undefined : role,
      location: location === 'All' ? undefined : location,
      demand_level: level === 'All' ? undefined : level,
    })
      .then((res) => setData(res.data))
      .catch(() => setError('Could not load market demand data. Is the FastAPI server running?'))
      .finally(() => setLoading(false));
  }, [sector, role, location, level]);

  const roles = useMemo(() => {
    const values = [...new Set((data.signals || []).map((x) => x.role))].sort();
    return ['All', ...values];
  }, [data.signals]);

  const locations = useMemo(() => {
    const values = [...new Set((data.signals || []).map((x) => x.location))].sort();
    return ['All', ...values];
  }, [data.signals]);

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">MARKET INTELLIGENCE · MAHARASHTRA</p>
          <h1>Market Demand Radar</h1>
          <p>See which skills are being signalled across roles, sectors and districts.</p>
        </div>
        <span className="status-badge">DEMO DATA</span>
      </div>

      <div className="filters" style={{display:'grid',gridTemplateColumns:'1.7fr 1.7fr 1fr 1fr',gap:12,marginBottom:20}}>
        <label>Sector<select value={sector} onChange={e=>setSector(e.target.value)}>{SECTORS.map(x=><option key={x}>{x}</option>)}</select></label>
        <label>Role<select value={role} onChange={e=>setRole(e.target.value)}>{roles.map(x=><option key={x}>{x}</option>)}</select></label>
        <label>Location<select value={location} onChange={e=>setLocation(e.target.value)}>{locations.map(x=><option key={x}>{x}</option>)}</select></label>
        <label>Demand<select value={level} onChange={e=>setLevel(e.target.value)}><option>All</option><option>high</option><option>medium</option><option>low</option></select></label>
      </div>

      {error && <div className="error-message">{error}</div>}
      <div className="kpi-grid" style={{gridTemplateColumns:'repeat(4,1fr)'}}>
        <div className="kpi-card"><span>Signals</span><strong>{data.total}</strong></div>
        <div className="kpi-card"><span>High demand</span><strong>{data.summary?.high || 0}</strong></div>
        <div className="kpi-card"><span>Medium demand</span><strong>{data.summary?.medium || 0}</strong></div>
        <div className="kpi-card"><span>Geography</span><strong>Maharashtra</strong></div>
      </div>

      <div className="panel" style={{marginTop:20}}>
        <div className="panel-header"><h2>Demand signals</h2><span>{loading ? 'Loading…' : `${data.total} records`}</span></div>
        {!loading && !data.signals?.length ? <div className="empty-state">No demand signals match these filters.</div> : (
          <div style={{overflowX:'auto'}}>
            <table className="data-table"><thead><tr><th>Sector</th><th>Role</th><th>Skill</th><th>Location</th><th>Demand</th><th>Evidence</th></tr></thead>
              <tbody>{(data.signals || []).map(row=><tr key={row.id}><td>{row.sector}</td><td>{row.role}</td><td><strong>{row.skill}</strong></td><td>{row.location}</td><td><span className={`status-badge ${row.demand_level}`}>{row.demand_level}</span></td><td><small>{row.source} · {row.source_date}<br/>{row.evidence}</small></td></tr>)}</tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
