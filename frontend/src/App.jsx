import { useState } from 'react';
import Sidebar from './components/Sidebar';
import DashboardSummary from './components/DashboardSummary';
import LeadsPanel from './components/LeadsPanel';
import ConversationsPanel from './components/ConversationsPanel';
import BookingsPanel from './components/BookingsPanel';
import RevenuePipeline from './components/RevenuePipeline';
import MissedOpportunities from './components/MissedOpportunities';
import ContentEngine from './components/ContentEngine';

const COMPONENTS = {
  summary: DashboardSummary,
  leads: LeadsPanel,
  conversations: ConversationsPanel,
  bookings: BookingsPanel,
  pipeline: RevenuePipeline,
  opportunities: MissedOpportunities,
  content: ContentEngine,
};

export default function App() {
  const [active, setActive] = useState('summary');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const Panel = COMPONENTS[active] || DashboardSummary;

  return (
    <div className="app-layout">
      <Sidebar
        active={active}
        onNavigate={(id) => { setActive(id); setSidebarOpen(false); }}
        isOpen={sidebarOpen}
      />
      <main className="main-content">
        {/* Mobile header */}
        <div style={{ display: 'none' }} className="mobile-header">
          <button
            className="mobile-nav-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h2 style={{ fontSize: '18px', fontWeight: 700 }}>LocalFlow</h2>
        </div>
        <Panel />
      </main>
    </div>
  );
}