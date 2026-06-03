import { useState, useEffect } from 'react';

const icons = {
  leads: '📋',
  conversations: '💬',
  bookings: '📅',
  pipeline: '📊',
  opportunities: '⚠️',
  content: '✨',
  summary: '📈',
};

const navItems = [
  { id: 'summary', label: 'Dashboard', icon: icons.summary },
  { id: 'leads', label: 'Leads', icon: icons.leads },
  { id: 'conversations', label: 'Conversations', icon: icons.conversations },
  { id: 'bookings', label: 'Bookings', icon: icons.bookings },
  { id: 'pipeline', label: 'Revenue Pipeline', icon: icons.pipeline },
  { id: 'opportunities', label: 'Missed Opportunities', icon: icons.opportunities, badge: 2 },
  { id: 'content', label: 'Content Engine', icon: icons.content },
];

export default function Sidebar({ active, onNavigate, isOpen }) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h1>
          <span>🌊</span> LocalFlow
        </h1>
        <div className="tagline">AI-Powered Lead Engine</div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
            {item.badge && <span className="nav-badge">{item.badge}</span>}
          </button>
        ))}
      </nav>
      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--color-border)', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
        LocalFlow v1.0
      </div>
    </aside>
  );
}