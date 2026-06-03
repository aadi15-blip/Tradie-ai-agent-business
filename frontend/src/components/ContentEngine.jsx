import { useState, useEffect } from 'react';
import { fetchContentIdeas } from '../api';

const PLATFORMS = ['Instagram', 'Facebook', 'Google Business'];

export default function ContentEngine() {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [platform, setPlatform] = useState('all');
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    fetchContentIdeas()
      .then(d => { setIdeas(d.ideas || []); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-state">Loading content ideas...</div>;
  if (error) return <div className="error-state">Could not load content ideas</div>;

  const filtered = platform === 'all'
    ? ideas
    : ideas.filter(i => i.platform === platform);

  const handleCopy = (text, id) => {
    navigator.clipboard?.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <>
      <div className="page-header">
        <h2>Content Engine</h2>
        <p>AI-generated content ideas to attract new customers</p>
      </div>

      <div className="panel-card">
        <div className="panel-card-body">
          <div className="content-tabs">
            <button
              className={`content-tab ${platform === 'all' ? 'active' : ''}`}
              onClick={() => setPlatform('all')}
            >
              All ({ideas.length})
            </button>
            {PLATFORMS.map(p => (
              <button
                key={p}
                className={`content-tab ${platform === p ? 'active' : ''}`}
                onClick={() => setPlatform(p)}
              >
                {p} ({ideas.filter(i => i.platform === p).length})
              </button>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✨</div>
              <h4>No content ideas yet</h4>
              <p>Generate new ideas with the AI Content Engine</p>
            </div>
          ) : (
            <div className="content-grid">
              {filtered.map(idea => (
                <div className="content-card" key={idea.id}>
                  <div className="cc-platform">
                    {idea.platform === 'Instagram' && '📸 '}
                    {idea.platform === 'Facebook' && '👍 '}
                    {idea.platform === 'Google Business' && '📍 '}
                    {idea.platform}
                  </div>
                  <div className="cc-hook">{idea.hook}</div>
                  <div className="cc-caption">{idea.caption}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                    <span className="cc-cta">{idea.cta}</span>
                    <button
                      className="btn btn-sm"
                      onClick={() => handleCopy(`${idea.hook}\n\n${idea.caption}\n\n${idea.cta}`, idea.id)}
                    >
                      {copiedId === idea.id ? '✅ Copied!' : '📋 Copy'}
                    </button>
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                    {idea.category}
                  </div>
                </div>
              ))}
            </div>
          )}

          {filtered.length > 0 && (
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button className="btn btn-primary">
                ✨ Generate More Ideas
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}