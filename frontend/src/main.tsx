import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, ArrowUpRight, Banknote, Bot, Check, ChevronRight, CircleDollarSign, Clock3, Command, Database, HandCoins, Inbox, LoaderCircle, LockKeyhole, Play, Radio, RefreshCw, ShieldCheck, Sparkles, UserRound, WalletCards, Zap } from 'lucide-react';
import './styles.css';

const API = 'http://localhost:8000';
type Ticket = { id:number; subject:string; type:string; status:string; requester:string; sku?:string|null; size?:string|null; qty?:number|null; };
type Event = { timestamp:string; trace_id:string; step:number; event:string; agent:string; detail:string; tool?:string|null; data?:Record<string, unknown>; };
type Agent = { key:string; name:string; tone:string; icon:string; role:string; blurb:string; };
const AGENTS: Agent[] = [
  {key:'boss',name:'Boss',tone:'violet',icon:'⌘',role:'Dispatch lead',blurb:'Routes the work and keeps the decision trail crisp.'},
  {key:'inventory',name:'Inventory',tone:'cyan',icon:'▦',role:'Stock control',blurb:'Checks SKU, size, quantity, and location.'},
  {key:'accounting',name:'Accounting',tone:'amber',icon:'$',role:'Money desk',blurb:'Verifies invoices, balances, and financial holds.'},
  {key:'facilities',name:'Facilities',tone:'green',icon:'⌂',role:'Lease watch',blurb:'Tracks rent timing and the shop’s physical commitments.'},
  {key:'customer_service',name:'Customer Service',tone:'rose',icon:'✦',role:'Voice of the shop',blurb:'Turns verified facts into a human-safe answer.'},
];

function App() {
  const [tickets,setTickets] = useState<Ticket[]>([]);
  const [selected,setSelected] = useState<number>(101);
  const [events,setEvents] = useState<Event[]>([]);
  const [balance,setBalance] = useState<number|null>(null);
  const [running,setRunning] = useState(false);
  const [message,setMessage] = useState('');
  const [approver,setApprover] = useState('');
  const [amount,setAmount] = useState('');
  const [kind,setKind] = useState<'payment'|'purchase'>('payment');
  const [approvalState,setApprovalState] = useState('');
  const eventsRef = useRef<HTMLDivElement>(null);
  const ticket = tickets.find(t => t.id === selected);
  const selectedEvents = useMemo(() => events.filter(e => !e.trace_id || e.trace_id === events.at(-1)?.trace_id || e.event === 'human_approval'), [events]);

  async function loadTickets() { const r=await fetch(`${API}/tickets`); if(r.ok) setTickets(await r.json()); }
  async function loadBalance() { const r=await fetch(`${API}/cash/balance`); if(r.ok) setBalance((await r.json()).balance); }
  async function loadEvents() { const r=await fetch(`${API}/events?limit=100`); if(r.ok) setEvents(await r.json()); }
  useEffect(() => { loadTickets(); loadBalance(); loadEvents(); }, []);
  useEffect(() => { eventsRef.current?.scrollTo({top:eventsRef.current.scrollHeight,behavior:'smooth'}); }, [events]);
  useEffect(() => { if(!running) return; const timer=window.setInterval(loadEvents,800); return()=>window.clearInterval(timer); }, [running]);

  async function runTicket() {
    setRunning(true); setMessage(''); setApprovalState(''); await loadEvents();
    try { const r=await fetch(`${API}/tickets/${selected}/run`,{method:'POST'}); const data=await r.json(); if(!r.ok) throw new Error(data.detail || 'Agent run failed'); setMessage(data.answer || 'Team completed the ticket.'); await loadTickets(); await loadEvents(); }
    catch(e) { setMessage(e instanceof Error ? e.message : 'Agent run failed.'); }
    finally { setRunning(false); }
  }
  async function approve() {
    const value=Number(amount); if(!approver.trim() || !value) { setApprovalState('Add an approver name and amount first.'); return; }
    setApprovalState('Sending human approval…');
    const r=await fetch(`${API}/approve-pay`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ticket_id:selected,amount:value,approved_by:approver,kind})});
    const data=await r.json(); if(!r.ok) { setApprovalState(data.detail || 'Approval failed.'); return; }
    setApprovalState(`Approved by ${data.approved_by}. Checking is now $${data.new_balance.toFixed(2)}.`); setBalance(data.new_balance); setAmount(''); await loadEvents();
  }
  const agentCounts = Object.fromEntries(AGENTS.map(a => [a.key, events.filter(e => e.agent === a.key).length]));
  const agentLatest = Object.fromEntries(AGENTS.map(a => [a.key, [...events].reverse().find(e => e.agent === a.key)?.detail || a.blurb]));
  return <div className="app-shell">
    <header className="topbar"><div className="brand"><div className="brand-mark"><Command size={18}/></div><div><p className="eyebrow">CAMPUS CUSTOMS / OPERATIONS</p><h1>Dispatch desk</h1></div></div><div className="top-actions"><span className="live-dot"><span/> MCP LINKED</span><button className="icon-button" onClick={()=>{loadTickets();loadBalance();loadEvents();}} title="Refresh"><RefreshCw size={17}/></button><div className="operator"><div className="avatar">M</div><span>Minahil<span>operator</span></span></div></div></header>
    <main className="workspace">
      <aside className="ticket-rail"><div className="rail-heading"><div><p className="eyebrow">INBOX / 03</p><h2>Open queue</h2></div><Inbox size={20}/></div><div className="queue-note"><Radio size={15}/> Live ticket feed</div><div className="ticket-list">{tickets.map(t=><button key={t.id} className={`ticket-card ${selected===t.id?'active':''}`} onClick={()=>setSelected(t.id)}><div className="ticket-top"><span className="ticket-id">#{t.id}</span><span className={`status ${t.status}`}>{t.status==='resolved'?<Check size={12}/>:<span className="status-dot"/>}{t.status}</span></div><strong>{t.subject}</strong><small>{t.requester}</small><div className="ticket-meta"><span>{t.type.replace('_',' ')}</span><ChevronRight size={15}/></div></button>)}</div><div className="rail-footer"><Database size={15}/><span><b>Working copy</b><br/>campus_customs_new.db</span></div></aside>
      <section className="main-column"><div className="section-kicker"><span>SELECTED TICKET</span><span className="rule"/><span className="updated"><Clock3 size={13}/> refreshed just now</span></div><div className="ticket-hero"><div><div className="hero-id">TICKET <b>#{ticket?.id ?? '—'}</b></div><h2>{ticket?.subject || 'Loading ticket…'}</h2><p>{ticket?.requester} · {ticket?.type?.replace('_',' ')}</p></div><div className="hero-action"><span className={`status large ${ticket?.status || 'open'}`}>{ticket?.status==='resolved'?<Check size={14}/>:<span className="status-dot"/>}{ticket?.status || 'loading'}</span><button className="run-button" disabled={running || ticket?.status==='resolved'} onClick={runTicket}>{running?<><LoaderCircle className="spin" size={17}/> Team working</>:<><Play size={16} fill="currentColor"/> Run agent team</>}</button></div></div><div className="fact-strip"><div><span>REQUEST</span><b>{ticket?.qty || 1} unit{ticket?.qty===1?'':'s'}</b></div><div><span>SKU</span><b>{ticket?.sku || '—'}</b></div><div><span>SIZE</span><b>{ticket?.size || '—'}</b></div><div><span>MODE</span><b><ShieldCheck size={14}/> Human guarded</b></div></div><div className="stream-head"><div><p className="eyebrow">LIVE TRACE</p><h3>Agent dialogue & actions</h3></div><span className="event-count"><Activity size={14}/> {events.length} events</span></div><div className="event-stream" ref={eventsRef}>{events.length===0?<div className="empty-stream"><Sparkles size={23}/><strong>Dispatch is ready</strong><span>Run a ticket to watch the MCP-backed team work.</span></div>:events.map((e,i)=><div className="event-row" key={`${e.timestamp}-${i}`}><div className={`event-icon ${e.agent}`}>{AGENTS.find(a=>a.key===e.agent)?.icon || (e.agent==='human'?'✓':'•')}</div><div className="event-body"><div className="event-line"><b>{AGENTS.find(a=>a.key===e.agent)?.name || e.agent}</b><span>{e.event.replaceAll('_',' ')}</span><time>{new Date(e.timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</time></div><p>{e.detail}</p>{e.tool&&<code><Zap size={12}/> MCP / {e.tool}</code>}</div></div>)}</div>{message&&<div className="result-banner"><Check size={17}/><span>{message}</span></div>}</section>
      <aside className="insight-rail"><div className="balance-card"><div className="balance-top"><span className="eyebrow">CHECKING BALANCE</span><Banknote size={20}/></div><strong>${balance===null?'—':balance.toLocaleString('en-US',{minimumFractionDigits:2})}</strong><span className="balance-caption"><CircleDollarSign size={14}/> Live from MCP · updates after approval</span></div><div className="panel agent-panel"><div className="panel-heading"><div><p className="eyebrow">TEAM ROSTER</p><h3>Who’s on deck</h3></div><span className="pulse">5 agents</span></div>{AGENTS.map(a=><div className="agent-row" key={a.key}><div className={`agent-badge ${a.tone}`}>{a.icon}</div><div className="agent-copy"><b>{a.name}</b><span>{a.role}</span><em>{agentLatest[a.key]}</em></div><span className="agent-count">{agentCounts[a.key] || 0}</span></div>)}</div><div className="panel approval-panel"><div className="panel-heading"><div><p className="eyebrow">HUMAN GATE</p><h3>Approve a transaction</h3></div><LockKeyhole size={18}/></div><p className="approval-copy">Agents can stage the decision. Only a human can move cash.</p><label>Approver name<input value={approver} onChange={e=>setApprover(e.target.value)} placeholder="Your name"/></label><label>Action<select value={kind} onChange={e=>setKind(e.target.value as 'payment'|'purchase')}><option value="payment">Payment</option><option value="purchase">Purchase</option></select></label><label>Amount to approve<input value={amount} onChange={e=>setAmount(e.target.value)} type="number" min="0" step="0.01" placeholder="0.00"/></label><button className="approve-button" onClick={approve}><HandCoins size={16}/> Approve for #{selected}</button>{approvalState&&<small className="approval-state">{approvalState}</small>}</div><div className="panel note-panel"><ArrowUpRight size={17}/><span><b>Desk note</b> Every action is appended to the audit trail so the next operator can pick up the thread.</span></div></aside>
    </main><footer><span><span className="footer-mark">◆</span> Campus Customs / Dispatch OS</span><span>FastAPI <b>●</b> MCP <b>●</b> human-in-the-loop</span></footer>
  </div>;
}
createRoot(document.getElementById('root')!).render(<App />);
