import { useState, useEffect } from 'react';
import { fetchBookings } from '../api';

const STATUS_ICONS = { confirmed: '✅', pending: '⏳', reminder_sent: '🔔' };
const STATUS_CLASS = { confirmed: 'badge-confirmed', pending: 'badge-pending', reminder_sent: 'badge-reminder' };
const STATUS_LABEL = { confirmed: 'Confirmed', pending: 'Pending', reminder_sent: 'Reminder Sent' };

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export default function BookingsPanel() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchBookings()
      .then(d => { setBookings(d.bookings || []); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  if (loading) return <div className="loading-state">Loading bookings...</div>;
  if (error) return <div className="error-state">Could not load bookings</div>;

  // Group bookings by date
  const grouped = {};
  bookings.forEach(b => {
    const d = b.date;
    if (!grouped[d]) grouped[d] = [];
    grouped[d].push(b);
  });

  const sortedDates = Object.keys(grouped).sort();

  return (
    <>
      <div className="page-header">
        <h2>Bookings</h2>
        <p>Upcoming appointments — {bookings.length} scheduled</p>
      </div>

      {bookings.length === 0 ? (
        <div className="panel-card">
          <div className="panel-card-body">
            <div className="empty-state">
              <div className="empty-icon">📅</div>
              <h4>No bookings yet</h4>
              <p>New bookings will appear here</p>
            </div>
          </div>
        </div>
      ) : (
        sortedDates.map(date => {
          const d = new Date(date + 'T12:00:00');
          const dayName = DAYS[d.getDay()];
          const dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
          return (
            <div className="panel-card" key={date}>
              <div className="panel-card-header">
                <h3>{dayName}, {dateStr}</h3>
                <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                  {grouped[date].length} appointment{grouped[date].length !== 1 ? 's' : ''}
                </span>
              </div>
              <div className="panel-card-body" style={{ padding: '12px 20px' }}>
                <div className="bookings-list">
                  {grouped[date].map(b => (
                    <div className="booking-item" key={b.id} style={{ borderLeftColor: b.status === 'confirmed' ? 'var(--color-green)' : b.status === 'pending' ? 'var(--color-yellow)' : 'var(--color-purple)' }}>
                      <div className="booking-time">{b.time}</div>
                      <div className="booking-info">
                        <div className="booking-name">{b.leadName}</div>
                        <div className="booking-detail">{b.service} · {b.phone}</div>
                      </div>
                      <span className={`badge ${STATUS_CLASS[b.status] || 'badge-pending'}`}>
                        {STATUS_ICONS[b.status]} {STATUS_LABEL[b.status] || b.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })
      )}
    </>
  );
}