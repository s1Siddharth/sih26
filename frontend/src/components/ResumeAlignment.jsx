import React, { useState } from 'react';
import { alignResume, fetchMarketRoles } from '../api/client';

export default function ResumeAlignment() {
  const [file, setFile] = useState(null);
  const [roleId, setRoleId] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [roles, setRoles] = useState([]);

  React.useEffect(() => {
    fetchMarketRoles().then(res => setRoles(res.data.roles || [])).catch(() => {});
  }, []);

  const analyze = async () => {
    if (!file) return setError('Upload a PDF or DOCX resume first.');
    setLoading(true); setError(''); setReport(null);
    try {
      const res = await alignResume(file, roleId || undefined);
      setReport(res.data.data);
      if (!roleId && res.data.data.target_role?.id) setRoleId(res.data.data.target_role.id);
    } catch (e) {
      setError(e.response?.data?.detail || 'Resume analysis failed. Check that the FastAPI server is running.');
    } finally { setLoading(false); }
  };

  const options = report?.role_options || [];

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">CANDIDATE TOOL · MAHARASHTRA</p>
          <h1>Resume–Market Alignment</h1>
          <p>Upload a resume to see how its skills align with a target market role.</p>
        </div>
        <span className="status-badge">PDF · DOCX</span>
      </div>

      <div className="panel">
        <div className="filters" style={{display:'grid',gridTemplateColumns:'1.5fr 1fr auto',gap:12,alignItems:'end'}}>
          <label>Resume
            <input type="file" accept=".pdf,.docx" onChange={e => {setFile(e.target.files?.[0] || null); setReport(null); setError('');}} />
          </label>
          <label>Target role
            <select value={roleId} onChange={e=>setRoleId(e.target.value)}>
              <option value="">Auto-detect best fit</option>
              {roles.map(r => <option key={r.role_id} value={r.role_id}>{r.role} · {r.sector}</option>)}
            </select>
          </label>
          <button className="primary-button" onClick={analyze} disabled={!file || loading}>{loading ? 'Analyzing…' : 'Analyze resume'}</button>
        </div>
        {file && <p style={{margin:'12px 0 0'}}>Selected: <strong>{file.name}</strong></p>}
        <p className="muted" style={{marginTop:8}}>Your file is processed temporarily. Maximum size: 5 MB.</p>
        {error && <div className="error-message" style={{marginTop:12}}>{error}</div>}
      </div>

      {report && <>
        <div className="kpi-grid" style={{gridTemplateColumns:'1.2fr 1fr 1fr 1fr',marginTop:20}}>
          <div className="kpi-card"><span>Market alignment</span><strong>{report.alignment_score}%</strong></div>
          <div className="kpi-card"><span>Matched skills</span><strong>{report.matched_skills.length}</strong></div>
          <div className="kpi-card"><span>Skill gaps</span><strong>{report.missing_skills.length}</strong></div>
          <div className="kpi-card"><span>Target role</span><strong style={{fontSize:'1rem'}}>{report.target_role.name}</strong></div>
        </div>

        <div className="panel" style={{marginTop:20}}>
          <div className="panel-header"><div><h2>{report.target_role.name}</h2><span>{report.target_role.sector}</span></div><span className="status-badge">Backend-scored</span></div>
          <div className="split-grid">
            <div><h3>Matched skills</h3><div className="tag-list">{report.matched_skills.length ? report.matched_skills.map(s=><span className="skill-tag" key={s}>✓ {s}</span>) : <span>None matched yet.</span>}</div></div>
            <div><h3>Skill gaps</h3><div className="tag-list">{report.missing_skills.length ? report.missing_skills.map(s=><span className="skill-tag gap" key={s}>! {s}</span>) : <span>No required skill gaps identified.</span>}</div></div>
          </div>
        </div>

        <div className="panel" style={{marginTop:20}}>
          <div className="panel-header"><h2>Score breakdown</h2><span>Deterministic rules</span></div>
          <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Component</th><th>Score</th></tr></thead><tbody>
            <tr><td>Required skill coverage</td><td>{report.score_breakdown.skill_coverage}%</td></tr>
            <tr><td>Experience evidence</td><td>{report.score_breakdown.experience_evidence}%</td></tr>
            <tr><td>Project evidence</td><td>{report.score_breakdown.project_evidence}%</td></tr>
            <tr><td><strong>Final alignment</strong></td><td><strong>{report.score_breakdown.final_score}%</strong></td></tr>
          </tbody></table></div>
        </div>

        <div className="panel" style={{marginTop:20}}>
          <div className="panel-header"><h2>What to improve</h2><span>{report.recommendations.length} actions</span></div>
          <ol className="recommendation-list">{report.recommendations.map((r,i)=><li key={i}>{r}</li>)}</ol>
        </div>

        <div className="panel" style={{marginTop:20}}>
          <div className="panel-header"><h2>Market evidence</h2><span>{report.evidence.length} signals</span></div>
          {report.evidence.length ? <div className="evidence-list">{report.evidence.slice(0,10).map((e,i)=><div className="evidence-item" key={i}><strong>{e.skill}</strong><span>{e.demand_level} · {e.source_type} · {e.source_date}</span><p>{e.evidence}</p></div>)}</div> : <div className="empty-state">No evidence signals available for this role.</div>}
        </div>
      </>}
    </section>
  );
}
