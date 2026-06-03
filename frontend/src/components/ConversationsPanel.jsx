import { useState, useEffect } from 'react';
import { fetchConversations } from '../api';
import { fetchLeads } from '../api';

export default function ConversationsPanel() {
  const [leads, setLeads] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msgLoading, setMsgLoading] = useState(false);

  useEffect(() => {
    fetchLeads()
      .then(d => { setLeads(d.leads || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setMsgLoading(true);
    fetchConversations(selectedId)
      .then(d => {
        setMessages(d.conversations || []);
        setMsgLoading(false);
      })
      .catch(() => setMsgLoading(false));
  }, [selectedId]);

  const selectedLead = leads.find(l => l.id === selectedId);

  if (loading) return <div className="loading-state">Loading conversations...</div>;

  const formatTime = (ts) => {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      <div className="page-header">
        <h2>Conversations</h2>
        <p>SMS conversations with your leads — auto-handled or manual</p>
      </div>

      <div className="panel-card">
        <div className="panel-card-body" style={{ display: 'flex', gap: 0, padding: 0 }}>
          {/* Lead list */}
          <div style={{ width: '280px', borderRight: '1px solid var(--color-border)', flexShrink: 0 }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', fontWeight: 600, fontSize: '14px' }}>
              Recent Chats
            </div>
            <div className="conversation-list" style={{ maxHeight: 420, overflowY: 'auto' }}>
              {leads.map(lead => (
                <div
                  key={lead.id}
                  className={`conversation-item ${selectedId === lead.id ? 'selected' : ''}`}
                  onClick={() => setSelectedId(lead.id)}
                >
                  <div className="conv-header">
                    <span className="conv-name">{lead.name}</span>
                    <span className={`badge badge-${lead.status === 'hot' ? 'hot' : lead.status === 'warm' ? 'warm' : 'cold'}`} style={{ fontSize: '10px', padding: '1px 6px' }}>
                      {lead.status}
                    </span>
                  </div>
                  <div className="conv-preview">{lead.service}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Chat view */}
          <div style={{ flex: 1 }}>
            {!selectedId ? (
              <div className="empty-state" style={{ padding: '60px 20px' }}>
                <div className="empty-icon">💬</div>
                <h4>Select a conversation</h4>
                <p>Choose a lead from the list to view messages</p>
              </div>
            ) : (
              <div className="chat-view">
                <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)', fontWeight: 600, fontSize: '14px' }}>
                  {selectedLead?.name} — {selectedLead?.service}
                  <span style={{ float: 'right', fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 400 }}>
                    {selectedLead?.phone}
                  </span>
                </div>
                {msgLoading ? (
                  <div className="loading-state" style={{ padding: '40px' }}>Loading messages...</div>
                ) : messages.length === 0 ? (
                  <div className="empty-state" style={{ padding: '40px' }}>
                    <div className="empty-icon">📭</div>
                    <h4>No messages yet</h4>
                    <p>This conversation hasn't started</p>
                  </div>
                ) : (
                  <div className="chat-messages">
                    {messages.map((msg, i) => (
                      <div key={i} className={`chat-msg ${msg.side}`}>
                        {msg.text}
                        <span className="msg-time">{formatTime(msg.time)}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div style={{ padding: '12px 16px', borderTop: '1px solid var(--color-border)', display: 'flex', gap: 8 }}>
                  <input
                    className="search-input"
                    placeholder="Type a reply... (AI auto-reply enabled)"
                    style={{ flex: 1 }}
                    readOnly
                  />
                  <button className="btn btn-primary" disabled>Send</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}