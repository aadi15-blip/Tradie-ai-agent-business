import { useState, useEffect } from 'react';
import { fetchPipeline } from '../api';

const STAGE_ORDER = ['New Leads', 'Contacted', 'Estimated', 'Booked', 'Job Started', 'Completed'];

export default function RevenuePipeline() {
  const [stages, setStages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchPipeline()
      .then(d => { setStages(d.stages || {}); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-state">Loading pipeline...</div>;
  if (error) return <div className="error-state">Could not load pipeline data</div>;

  const stageKeys = STAGE_ORDER.filter(s => stages[s]);
  const totalValue = stageKeys.reduce((sum, s) => sum + (stages[s].value || 0), 0);

  return (
    <>
      <div className="page-header">
        <h2>Revenue Pipeline</h2>
        <p>${totalValue.toLocaleString()} total pipeline value</p>
      </div>

      <div className="panel-card">
        <div className="panel-card-body">
          <div className="pipeline-container">
            {stageKeys.map((name, i) => {
              const stage = stages[name];
              const stageTotal = stageKeys.slice(i).reduce((s, k) => s + (stages[k].count || 0), 0);
              return (
                <div className="pipeline-stage" key={name}>
                  <h4>{name}</h4>
                  <div className="pipeline-count">{stage.count}</div>
                  <div style={{ textAlign: 'center', marginBottom: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-green)' }}>
                      ${(stage.value || 0).toLocaleString()}
                    </span>
                  </div>
                  {/* Mini funnel connector */}
                  {i < stageKeys.length - 1 && (
                    <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                      ↓ {stageTotal} leads ahead
                    </div>
                  )}
                  {/* Sample cards */}
                  {name === 'New Leads' && (
                    <>
                      <div className="pipeline-card">
                        <div className="pc-name">Mike J. · Roof Repair</div>
                        <div className="pc-value">$4,500</div>
                      </div>
                      <div className="pipeline-card">
                        <div className="pc-name">Emily D. · Electrical</div>
                        <div className="pc-value">$1,800</div>
                      </div>
                    </>
                  )}
                  {name === 'Contacted' && (
                    <div className="pipeline-card">
                      <div className="pc-name">Sarah C. · HVAC</div>
                      <div className="pc-value">$2,800</div>
                    </div>
                  )}
                  {name === 'Booked' && (
                    <>
                      <div className="pipeline-card">
                        <div className="pc-name">Mike J. · Roof Repair</div>
                        <div className="pc-value">$4,500</div>
                      </div>
                      <div className="pipeline-card">
                        <div className="pc-name">Lisa P. · Landscaping</div>
                        <div className="pc-value">$3,200</div>
                      </div>
                    </>
                  )}
                  {name === 'Completed' && (
                    <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--color-text-secondary)', padding: '8px' }}>
                      ${(stage.value || 0).toLocaleString()} this period
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Summary bar */}
          <div style={{ marginTop: '20px', padding: '16px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>TOTAL PIPELINE</div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-primary)' }}>${totalValue.toLocaleString()}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>LEADS IN PIPELINE</div>
                <div style={{ fontSize: '24px', fontWeight: 700 }}>{stageKeys.reduce((s, k) => s + (stages[k].count || 0), 0)}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>COMPLETED THIS MONTH</div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-green)' }}>{stages['Completed']?.count || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}