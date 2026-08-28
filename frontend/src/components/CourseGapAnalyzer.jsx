import React, { useEffect, useState } from 'react';
import { fetchCourses, fetchCourseMarketRoles, fetchCourseMarketGap } from '../api/client';

export default function CourseGapAnalyzer() {
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [roles, setRoles] = useState([]);
  const [roleId, setRoleId] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourses().then(({ data }) => setCourses(data.courses || [])).catch(() => setError('Could not load courses.'));
  }, []);

  useEffect(() => {
    if (!courseId) { setRoles([]); setRoleId(''); setReport(null); return; }
    setError('');
    fetchCourseMarketRoles(courseId)
      .then(({ data }) => {
        setRoles(data.roles || []);
        setRoleId(data.roles?.[0]?.role_id || '');
      })
      .catch(() => setError('Could not load market roles for this course.'));
  }, [courseId]);

  const analyze = async () => {
    if (!courseId) return;
    setLoading(true); setError('');
    try {
      const { data } = await fetchCourseMarketGap(courseId, roleId);
      setReport(data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Analysis failed.');
    } finally { setLoading(false); }
  };

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">CURRICULUM ALIGNMENT · MAHARASHTRA</p>
          <h1>Course–Market Gap Analyzer</h1>
          <p>Compare what a course teaches with the skills a target market role requires.</p>
        </div>
        <span className="status-badge">DETERMINISTIC</span>
      </div>

      <div className="panel">
        <div className="panel-header"><h2>Choose a course</h2><span>Market data: demo corpus</span></div>
        <div className="filters" style={{display:'grid',gridTemplateColumns:'1.5fr 1.5fr auto',gap:12,alignItems:'end'}}>
          <label>Course<select value={courseId} onChange={e=>setCourseId(e.target.value)}><option value="">Select course</option>{courses.map(c=><option key={c.id} value={c.id}>{c.trade_name} · {c.district}</option>)}</select></label>
          <label>Target market role<select value={roleId} onChange={e=>setRoleId(e.target.value)} disabled={!roles.length}><option value="">Auto-select best fit</option>{roles.map(r=><option key={r.role_id} value={r.role_id}>{r.role} · {Math.round(r.alignment_score)}% fit</option>)}</select></label>
          <button className="primary-button" onClick={analyze} disabled={!courseId || loading}>{loading ? 'Analyzing…' : 'Analyze gap'}</button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </div>

      {report && (
        <>
          <div className="kpi-grid" style={{gridTemplateColumns:'1.2fr 1fr 1fr 1fr',marginTop:20}}>
            <div className="kpi-card"><span>Market alignment</span><strong>{report.alignment_score}%</strong></div>
            <div className="kpi-card"><span>Matched</span><strong>{report.matched_skills.length}</strong></div>
            <div className="kpi-card"><span>Skill gaps</span><strong>{report.missing_skills.length}</strong></div>
            <div className="kpi-card"><span>Recommended action</span><strong style={{fontSize:'1rem'}}>{report.recommended_action}</strong></div>
          </div>

          <div className="panel" style={{marginTop:20}}>
            <div className="panel-header"><div><h2>{report.course.trade_name} → {report.target_role.name}</h2><span>{report.course.district} · {report.target_role.sector}</span></div><span className="status-badge">{report.priority} priority</span></div>
            <div className="split-grid">
              <div><h3>Matched skills</h3><div className="tag-list">{report.matched_skills.map(s=><span className="skill-tag" key={s}>✓ {s}</span>)}</div></div>
              <div><h3>Priority skill gaps</h3><div className="tag-list">{report.missing_skills.length ? report.missing_skills.map(s=><span className="skill-tag gap" key={s}>! {s}</span>) : <span>None identified for this role.</span>}</div></div>
            </div>
          </div>

          <div className="panel" style={{marginTop:20}}>
            <div className="panel-header"><h2>Recommended action</h2><strong>{report.recommended_action}</strong></div>
            <ol className="recommendation-list">{report.recommendations.map((r,i)=><li key={i}>{r}</li>)}</ol>
          </div>

          <div className="panel" style={{marginTop:20}}>
            <div className="panel-header"><h2>Skill comparison</h2><span>Score is calculated by backend rules</span></div>
            <div style={{overflowX:'auto'}}><table className="data-table"><thead><tr><th>Skill</th><th>Status</th><th>Demand</th><th>Required</th></tr></thead><tbody>{report.skill_comparison.map(x=><tr key={x.skill_id}><td><strong>{x.skill}</strong></td><td>{x.status === 'matched' ? '✓ Matched' : '⚠ Gap'}</td><td>{x.demand_level}</td><td>{x.required_proficiency}</td></tr>)}</tbody></table></div>
          </div>

          <div className="panel" style={{marginTop:20}}>
            <div className="panel-header"><h2>Evidence</h2><span>{report.evidence.length} signals</span></div>
            {report.evidence.length ? <div className="evidence-list">{report.evidence.slice(0,8).map((e,i)=><div className="evidence-item" key={i}><strong>{e.skill}</strong><span>{e.source_type} · {e.source_date}</span><p>{e.evidence}</p></div>)}</div> : <div className="empty-state">No evidence signals were available for this role.</div>}
          </div>
        </>
      )}
    </section>
  );
}
