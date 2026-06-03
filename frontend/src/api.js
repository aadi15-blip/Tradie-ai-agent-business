/**
 * API client for LocalFlow backend.
 * Falls back to mock data when backend is unavailable.
 */

const API_BASE = 'http://localhost:8200';

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_DATA = {
  leads: [
    { id: 'L001', name: 'Mike Johnson', phone: '(555) 234-5678', service: 'Roof Repair', source: 'Google Ads', status: 'hot', score: 92, tags: ['roofing', 'emergency'], created: '2025-05-26T08:30:00Z', value: 4500 },
    { id: 'L002', name: 'Sarah Chen', phone: '(555) 876-5432', service: 'HVAC Tune-Up', source: 'Referral', status: 'warm', score: 74, tags: ['hvac', 'seasonal'], created: '2025-05-25T14:15:00Z', value: 2800 },
    { id: 'L003', name: 'Tom Martinez', phone: '(555) 345-6789', service: 'Plumbing', source: 'Website', status: 'cold', score: 35, tags: ['plumbing'], created: '2025-05-24T10:00:00Z', value: 1200 },
    { id: 'L004', name: 'Lisa Park', phone: '(555) 456-7890', service: 'Landscaping', source: 'Instagram', status: 'hot', score: 88, tags: ['landscaping', 'spring'], created: '2025-05-26T09:45:00Z', value: 3200 },
    { id: 'L005', name: 'David Wilson', phone: '(555) 567-8901', service: 'Paint Exterior', source: 'Facebook', status: 'warm', score: 65, tags: ['painting'], created: '2025-05-23T16:30:00Z', value: 5100 },
    { id: 'L006', name: 'Emily Davis', phone: '(555) 678-9012', service: 'Electrical', source: 'Google Ads', status: 'hot', score: 95, tags: ['electrical', 'emergency'], created: '2025-05-26T11:00:00Z', value: 1800 },
    { id: 'L007', name: 'Robert Kim', phone: '(555) 789-0123', service: 'Roof Replacement', source: 'Referral', status: 'warm', score: 71, tags: ['roofing'], created: '2025-05-22T09:00:00Z', value: 8500 },
    { id: 'L008', name: 'Angela White', phone: '(555) 890-1234', service: 'Gutter Cleaning', source: 'Website', status: 'cold', score: 28, tags: ['cleaning', 'spring'], created: '2025-05-20T13:00:00Z', value: 600 },
  ],

  conversations: {
    'L001': [
      { side: 'incoming', text: 'Hi, my roof is leaking after the storm last night. Can you help?', time: '2025-05-26T08:32:00Z' },
      { side: 'outgoing', text: 'Hi Mike, I\'m sorry to hear about the leak! We can send someone out today. Are you free this afternoon around 2pm?', time: '2025-05-26T08:32:45Z' },
      { side: 'incoming', text: 'Yes, 2pm works. My address is 123 Oak Street.', time: '2025-05-26T08:33:30Z' },
      { side: 'outgoing', text: 'Perfect! I\'ve booked you for today at 2pm. Our technician Tom will call you 30 minutes before arrival.', time: '2025-05-26T08:34:00Z' },
    ],
    'L002': [
      { side: 'incoming', text: 'Looking to get my AC serviced before summer hits.', time: '2025-05-25T14:15:00Z' },
      { side: 'outgoing', text: 'Great idea, Sarah! We have a summer tune-up special — $149 for a full HVAC check. Interested?', time: '2025-05-25T14:16:00Z' },
      { side: 'incoming', text: 'That sounds good. Can you come Thursday morning?', time: '2025-05-25T14:17:30Z' },
    ],
    'L003': [
      { side: 'outgoing', text: 'Hi Tom! Thanks for reaching out about the plumbing issue. Could you tell me more about what\'s happening?', time: '2025-05-24T10:05:00Z' },
      { side: 'incoming', text: 'Kitchen sink drain is clogged.', time: '2025-05-24T11:30:00Z' },
      { side: 'outgoing', text: 'Got it! We can schedule a visit. When works best for you?', time: '2025-05-24T11:31:00Z' },
    ],
  },

  bookings: [
    { id: 'B001', leadName: 'Mike Johnson', service: 'Roof Repair', date: '2025-05-26', time: '14:00', status: 'confirmed', phone: '(555) 234-5678' },
    { id: 'B002', leadName: 'Lisa Park', service: 'Landscaping Design', date: '2025-05-27', time: '09:00', status: 'confirmed', phone: '(555) 456-7890' },
    { id: 'B003', leadName: 'Emily Davis', service: 'Electrical Repair', date: '2025-05-27', time: '11:00', status: 'pending', phone: '(555) 678-9012' },
    { id: 'B004', leadName: 'David Wilson', service: 'Painting Estimate', date: '2025-05-28', time: '10:00', status: 'reminder_sent', phone: '(555) 567-8901' },
    { id: 'B005', leadName: 'Robert Kim', service: 'Roof Inspection', date: '2025-05-29', time: '13:00', status: 'confirmed', phone: '(555) 789-0123' },
  ],

  pipeline: {
    'New Leads': { count: 8, value: 12700 },
    'Contacted': { count: 5, value: 8700 },
    'Estimated': { count: 3, value: 9500 },
    'Booked': { count: 4, value: 12300 },
    'Job Started': { count: 2, value: 7300 },
    'Completed': { count: 6, value: 18400 },
  },

  missedOpportunities: [
    { type: 'missed_call', leadName: 'Carlos Rivera', phone: '(555) 111-2233', detail: 'Missed call at 8:47 AM today', value: null },
    { type: 'unresponsive', leadName: 'Jennifer Hayes', phone: '(555) 222-3344', detail: 'No reply after 3 SMS attempts', value: 3400 },
    { type: 'lost', leadName: 'Steve Adams', phone: '(555) 333-4455', detail: 'Chose competitor (lower price)', value: 6200 },
    { type: 'missed_call', leadName: 'Patricia Lee', phone: '(555) 444-5566', detail: 'Missed call at 6:15 PM yesterday', value: null },
    { type: 'unresponsive', leadName: 'Brian Taylor', phone: '(555) 555-6677', detail: 'Lead went cold after initial quote', value: 2800 },
    { type: 'lost', leadName: 'Megan Foster', phone: '(555) 666-7788', detail: 'Not ready to commit — follow up in 3 months', value: 1500 },
  ],

  contentIdeas: [
    { id: 'C01', platform: 'Instagram', hook: 'Your roof has a secret life 🌧️', caption: 'Did you know a small leak can cause $10K+ in hidden damage? Catching it early saves thousands. Book a free inspection today.', cta: 'Book Free Inspection', category: 'Educational' },
    { id: 'C02', platform: 'Instagram', hook: 'Before & After: 2-day kitchen reno 🏠', caption: 'From outdated to stunning in just 48 hours. Our team transformed this kitchen with new counters, backsplash, and hardware.', cta: 'Get a Quote', category: 'Showcase' },
    { id: 'C03', platform: 'Facebook', hook: '⚠️ Summer is coming. Is your AC ready?', caption: 'Don\'t wait until the first heatwave. Our $149 summer tune-up keeps your AC running all season. Limited availability!', cta: 'Book Tune-Up', category: 'Seasonal' },
    { id: 'C04', platform: 'Google Business', hook: '★ 4.9 stars — 200+ reviews and counting', caption: 'Local homeowners trust us for quality work, transparent pricing, and same-day service. See why our neighbors love us.', cta: 'Read Reviews', category: 'Social Proof' },
    { id: 'C05', platform: 'Instagram', hook: '3 signs your pipes are failing 🚰', caption: 'Discolored water, low pressure, and strange noises. If you notice any of these, call a plumber ASAP to prevent a burst pipe.', cta: 'Call Now', category: 'Educational' },
    { id: 'C06', platform: 'Facebook', hook: 'Spring cleaning: don\'t forget your gutters 🍂', caption: 'Clogged gutters cause roof damage, foundation issues, and pest problems. Our gutter cleaning service starts at just $99.', cta: 'Book Cleaning', category: 'Seasonal' },
    { id: 'C07', platform: 'Google Business', hook: 'Same-day service available in your area', caption: 'Emergency roof repair? Burst pipe? No power? We respond within 2 hours for emergencies. Local, licensed, insured.', cta: 'Call for Emergency', category: 'Service' },
    { id: 'C08', platform: 'Instagram', hook: 'Meet the team behind the work 👷‍♂️', caption: 'Certified, background-checked, and trained. Every LocalFlow partner goes through rigorous vetting so you get the best.', cta: 'Learn More', category: 'Team' },
  ],

  summary: {
    totalLeads: 48,
    conversionRate: 32,
    avgResponseTime: '47s',
    bookingsThisWeek: 12,
    pipelineValue: 68900,
    leadsTrend: '+12%',
    conversionTrend: '+5%',
    responseTrend: '-8s',
    bookingsTrend: '+3',
    pipelineTrend: '+$8,200',
  },
};

// ─── API Helper ──────────────────────────────────────────────────────────────

async function fetchJson(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      signal: AbortSignal.timeout(3000),
      ...options,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return null;
  }
}

// ─── Public API ──────────────────────────────────────────────────────────────

export async function fetchSummary() {
  const data = await fetchJson(`${API_BASE}/api/summary`);
  return data || { ...MOCK_DATA.summary };
}

export async function fetchLeads() {
  const data = await fetchJson(`${API_BASE}/api/leads`);
  return data || { leads: [...MOCK_DATA.leads] };
}

export async function fetchConversations(leadId) {
  const data = await fetchJson(`${API_BASE}/api/conversations/${leadId}`);
  return data || { conversations: MOCK_DATA.conversations[leadId] || [] };
}

export async function fetchBookings() {
  const data = await fetchJson(`${API_BASE}/api/bookings`);
  return data || { bookings: [...MOCK_DATA.bookings] };
}

export async function fetchPipeline() {
  const data = await fetchJson(`${API_BASE}/api/pipeline`);
  return data || { stages: MOCK_DATA.pipeline };
}

export async function fetchMissedOpportunities() {
  const data = await fetchJson(`${API_BASE}/api/opportunities`);
  return data || { opportunities: [...MOCK_DATA.missedOpportunities] };
}

export async function fetchContentIdeas() {
  const data = await fetchJson(`${API_BASE}/api/content`);
  return data || { ideas: [...MOCK_DATA.contentIdeas] };
}