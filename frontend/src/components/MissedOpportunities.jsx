import { useState, useEffect } from 'react';
import { fetchMissedOpportunities } from '../api';

const TYPE_ICONS = { missed_call: '📞', unresponsive: '💤', lost: '❌' };
const TYPE_LABELS = { missed_call: 'Missed Call', unresponsive: 'Unresponsive', lost: 'Lost Deal' };
const TYPE_CLASS = { missed_call: 'missed-call', unresponsive: 'unresponsive', lost: 'lost' };

export default function MissedOpportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchMissedOpportunities()
      .then(d => { setOpportunities(d.opportunities || []); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-state">Loading opportunities...</div>;
  if (error) return <div className="error-state">Could not load data</div>;

  const totalLostValue = opportunities
    .filter(o => o.type === 'lost' || o.type === 'unresponsive')
    .reduce((sum, o) => sum + (o.value || 0), 0);

  return (
    <>
      <div className="page-header">
        <h2>Missed Opportunities</h2>
        <p>${totalLostValue.toLocaleString()} in potential revenue at risk · {opportunities.length} items</p>
      </div>

      <div className="panel-card">
        <div className="panel-card-body" style={{ padding: 0 }}>
          {opportunities.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🎉</div>
              <h4>No missed opportunities</h4>
              <p>You're catching every lead! Great job.</p>
            </div>
          ) : (
            opportunities.map((opp, i) => (
              <div className="opportunity-item" key={i}>
                <div className={`opp-icon ${TYPE_CLASS[opp.type]}`}>
                  {TYPE_ICONS[opp.type]}
                </div>
                <div className="opp-info">
                  <div className="opp-title">{opp.leadName}</div>
                  <div className="opp-detail">
                    {TYPE_LABELS[opp.type]} · {opp.detail}
                    {opp.phone && <span> · {opp.phone}</span>}
                  </div>
                </div>
                {opp.value && (
                  <div className="opp-value">${opp.value.toLocaleString()}</div>
                )}
                <button className="btn btn-sm btn-primary" style={{ flexShrink: 0 }}>
                  {opp.type === 'missed_call' ? 'Call Back' : opp.type === 'unresponsive' ? 'Re-engage' : 'Analyze'}
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Summary stats */}
      <div className="kpi-grid" style={{ marginTop: '8px' }}>
        <div className="kpi-card">
          <div className="kpi-label">Missed Calls</div>
          <div className="kpi-value" style={{ color: 'var(--color-red)' }}>
            {opportunities.filter(o => o.type === 'missed_call').length}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Unresponsive Leads</div>
          <div className="kpi-value" style={{ color: 'var(--color-yellow)' }}>
            {opportunities.filter(o => o.type === 'unresponsive').length}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Lost Deals</div>
          <div className="kpi-value" style={{ color: 'var(--color-red)' }}>
            {opportunities.filter(o => o.type === 'lost').length}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">At-Risk Revenue</div>
          <div className="kpi-value" style={{ color: 'var(--color-red)' }}>
            ${totalLostValue.toLocaleString()}
          </div>
        </div>
      </div>
    </>
  );
}