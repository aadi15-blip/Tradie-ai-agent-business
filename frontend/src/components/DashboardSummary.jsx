import { useState, useEffect } from 'react';
import { fetchSummary } from '../api';

export default function DashboardSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchSummary()
      .then(d => { if (mounted) { setData(d); setLoading(false); } })
      .catch(() => { if (mounted) { setError(true); setLoading(false); } });
    return () => { mounted = false; };
  }, []);

  if (loading) return <div className="loading-state">Loading dashboard...</div>;
  if (error) return <div className="error-state">Could not load dashboard data</div>;
  if (!data) return null;

  const cards = [
    { label: 'Total Leads', value: data.totalLeads, change: data.leadsTrend, up: true },
    { label: 'Conversion Rate', value: `${data.conversionRate}%`, change: data.conversionTrend, up: true },
    { label: 'Avg Response Time', value: data.avgResponseTime, change: data.responseTrend, up: false },
    { label: 'Bookings This Week', value: data.bookingsThisWeek, change: data.bookingsTrend, up: true },
    { label: 'Pipeline Value', value: `$${data.pipelineValue?.toLocaleString()}`, change: data.pipelineTrend, up: true },
  ];

  return (
    <>
      <div className="page-header">
        <h2>Dashboard Overview</h2>
        <p>Your business at a glance</p>
      </div>
      <div className="kpi-grid">
        {cards.map((card, i) => (
          <div className="kpi-card" key={i}>
            <div className="kpi-label">{card.label}</div>
            <div className="kpi-value">{card.value}</div>
            <div className={`kpi-change ${card.up ? 'up' : 'down'}`}>
              {card.change}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}