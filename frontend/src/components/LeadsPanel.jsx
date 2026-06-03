import { useState, useEffect } from 'react';
import { fetchLeads } from '../api';

export default function LeadsPanel() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    let mounted = true;
    fetchLeads()
      .then(d => { if (mounted) { setLeads(d.leads || []); setLoading(false); } })
      .catch(() => { if (mounted) { setError(true); setLoading(false); } });
    return () => { mounted = false; };
  }, []);

  if (loading) return <div className="loading-state">Loading leads...</div>;
  if (error) return <div className="error-state">Could not load leads</div>;

  const filtered = leads.filter(lead => {
    const matchesSearch = search === '' ||
      lead.name?.toLowerCase().includes(search.toLowerCase()) ||
      lead.service?.toLowerCase().includes(search.toLowerCase()) ||
      lead.phone?.includes(search);
    const matchesFilter = filter === 'all' || lead.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <>
      <div className="page-header">
        <h2>Leads</h2>
        <p>{leads.length} total leads · Track and manage every opportunity</p>
      </div>

      <div className="panel-card">
        <div className="panel-card-body">
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <input
              className="search-input"
              style={{ flex: 1, minWidth: 200 }}
              placeholder="Search by name, service, or phone..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          <div className="filter-bar">
            {['all', 'hot', 'warm', 'cold'].map(f => (
              <button
                key={f}
                className={`filter-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <h4>No leads found</h4>
              <p>Try a different search or filter</p>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Service</th>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Value</th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(lead => (
                  <tr key={lead.id}>
                    <td>
                      <strong>{lead.name}</strong>
                      <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{lead.phone}</div>
                    </td>
                    <td>{lead.service}</td>
                    <td>{lead.source}</td>
                    <td>
                      <span className={`badge badge-${lead.status === 'hot' ? 'hot' : lead.status === 'warm' ? 'warm' : 'cold'}`}>
                        <span className={`badge-dot ${lead.status}`}></span>
                        {lead.status.charAt(0).toUpperCase() + lead.status.slice(1)}
                      </span>
                    </td>
                    <td>
                      <div className="score-bar">
                        <span style={{ fontWeight: 600, fontSize: '13px', minWidth: '30px' }}>{lead.score}</span>
                        <div className="score-bar-fill">
                          <div className="fill" style={{
                            width: `${lead.score}%`,
                            background: lead.score >= 80 ? 'var(--color-green)' : lead.score >= 50 ? 'var(--color-yellow)' : 'var(--color-red)'
                          }}></div>
                        </div>
                      </div>
                    </td>
                    <td>${lead.value?.toLocaleString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {lead.tags?.map(tag => (
                          <span key={tag} style={{
                            background: 'var(--color-bg)',
                            padding: '2px 8px',
                            borderRadius: '10px',
                            fontSize: '11px',
                            fontWeight: 500,
                            color: 'var(--color-text-secondary)'
                          }}>{tag}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}