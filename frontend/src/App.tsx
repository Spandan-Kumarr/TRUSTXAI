import { useCallback, useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { Activity, ArrowUp, BookOpen, Check, ChevronDown, ChevronRight, CircleHelp, Clipboard, Download, FileText, LoaderCircle, Menu, MessageSquare, Monitor, Moon, PanelLeftClose, PanelRight, Pencil, Plus, Search, ShieldCheck, SlidersHorizontal, Square, Sun, Trash2, Upload, X } from 'lucide-react';
import { api, jsonBody } from './api';
import { useDrawerFocus } from './useDrawerFocus';
import type { Analysis, CaseInput, CaseSummary, ClinicalCase, Example, Message, Mode, Options, Runtime, Source } from './types';

const EMPTY_OPTIONS: Options = { A: '', B: '', C: '', D: '' };
const OPTION_KEYS = ['A', 'B', 'C', 'D'] as const;
const DEFAULT_QUESTION = 'What is the most likely diagnosis?';
const isBusy = (item: ClinicalCase | null) => !!item && ['queued', 'running', 'cancelling'].includes(item.status);
const pretty = (value: unknown) => JSON.stringify(value, null, 2) ?? 'Not recorded';
const errorText = (error: unknown) => error instanceof Error ? error.message : typeof error === 'string' ? error : pretty(error);
const readable = (value: unknown): string => typeof value === 'string' ? value.replaceAll('_', ' ') : value === true ? 'Yes' : value === false ? 'No' : value == null ? 'Not recorded' : pretty(value);
const safeUrl = (value?: string) => { try { const url = new URL(value ?? ''); return ['http:', 'https:'].includes(url.protocol) ? url.href : undefined; } catch { return undefined; } };

function Mark({ small = false }: { small?: boolean }) {
  return <span className={small ? 'brand-mark small' : 'brand-mark'} aria-hidden="true"><span /><span /><span /><span /></span>;
}

function Dialog({ title, children, onClose, footer }: { title: string; children: ReactNode; onClose: () => void; footer?: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { const dialog = ref.current; dialog?.showModal(); return () => { dialog?.close(); }; }, []);
  return <dialog ref={ref} className="modal" aria-labelledby="dialog-title" onCancel={onClose} onClick={event => { if (event.target === event.currentTarget) { const box = event.currentTarget.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) onClose(); } }}>
    <div className="modal-header"><h2 id="dialog-title">{title}</h2><button className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={19} /></button></div>
    <div className="modal-body">{children}</div>
    {footer && <div className="modal-footer">{footer}</div>}
  </dialog>;
}

function SourceDetails({ source }: { source: Source }) {
  const href = safeUrl(source.url);
  return <article className="source-card"><div className="source-meta"><BookOpen size={16} /><span>{source.category ? readable(source.category) : 'Recorded source'}</span>{source.content_type === 'curated_source_summary' && <span>· Curated source summary</span>}</div><h3>{source.title}</h3>{source.content && <p className="source-content">{source.content}</p>}{href && <a href={href} target="_blank" rel="noreferrer">Open source ↗</a>}{source.verification != null && <details><summary>Source verification</summary><pre className="code-block">{pretty(source.verification)}</pre></details>}</article>;
}

function ResultCard({ result, onAudit, onCopy }: { result: Analysis; onAudit: () => void; onCopy: (text: string) => void }) {
  const [view, setView] = useState<'novice' | 'expert'>('novice');
  const decision = result.evidence?.decision;
  const explanation = result.views?.[view];
  const titles = view === 'novice' ? ['The recorded suggestion', 'What changed when a finding was omitted', 'How much was checked', 'What this means'] : ['Model decision', 'Selected omission', 'Coverage and recheck', 'Interpretation limits'];
  return <div className="result-card">
    <div className="result-heading"><span className="decision-badge">{decision?.label || '—'}</span><div><div className="eyebrow">MODEL-SELECTED OPTION</div><h2>{decision?.name || 'See the recorded model output'}</h2></div></div>
    <p className="review-note"><ShieldCheck size={15} /> A model suggestion for review, not a verified diagnosis.</p>
    <div className="view-toggle" role="group" aria-label="Explanation detail"><button className={view === 'novice' ? 'active' : ''} onClick={() => setView('novice')}>Simple explanation</button><button className={view === 'expert' ? 'active' : ''} onClick={() => setView('expert')}>Technical explanation</button></div>
    <div className="explanation-block">{explanation ? Object.entries(explanation).map(([key, value], index) => <section className="explanation-item" key={key}><h3 className="explanation-title">{titles[index] || key}</h3><p>{value}</p></section>) : <p>The explanation is not available. Open the evidence audit to inspect the recorded output.</p>}</div>
    {result.release_status === 'evidence_template' && <div className="grounded-status"><FileText size={14} /> Evidence template used. Review explanation-check details in the audit.</div>}
    <div className="message-actions"><button className="text-button" onClick={onAudit}><PanelRight size={15} /> View evidence</button><button className="icon-button" title="Copy explanation" aria-label="Copy explanation" onClick={() => onCopy(Object.values(explanation ?? {}).join('\n\n'))}><Clipboard size={15} /></button></div>
  </div>;
}

function UserInput({ input, onEdit }: { input: CaseInput; onEdit: () => void }) {
  if (input.kind === 'chat') return <p className="message-bubble">{input.text || input.case_text}</p>;
  return <div className="message-bubble case-input-preview"><p>{input.case_text}</p><p className="input-question">{input.question}</p><div className="option-list">{OPTION_KEYS.map(key => input.options?.[key] && <div key={key}><span>{key}</span>{input.options[key]}</div>)}</div><button className="text-button" onClick={onEdit}><Pencil size={13} /> Edit as a new case</button></div>;
}

function Answer({ message, onSource }: { message: Message; onSource: (source: Source) => void }) {
  const payload = message.payload;
  const label = payload.grounding_status === 'source_checked' ? 'Source checked' : payload.grounding_status === 'source_passages' ? 'Retrieved source passages' : payload.grounding_status === 'insufficient_sources' ? 'Insufficient source support' : null;
  return <><div className="answer-text">{payload.text || 'No answer text was recorded.'}</div>{label && <div className="grounded-status"><BookOpen size={14} />{label}</div>}{!!payload.citations?.length && <div className="citations">{payload.citations.map((source, index) => <button className="citation-button" key={`${source.id || source.title}-${index}`} onClick={() => onSource(source)}><span>{source.citation_number ?? index + 1}</span>{source.title}<ChevronRight size={13} /></button>)}</div>}</>;
}

function EvidencePanel({ item, runtime, onClose, highlight }: { item: ClinicalCase | null; runtime: Runtime | null; onClose: () => void; highlight: string | null }) {
  const panelRef = useRef<HTMLElement>(null);
  const isModal = useDrawerFocus(true, panelRef, '(max-width: 900px)', ['.workspace', '.sidebar']);
  const result = item?.result;
  const evidence = result?.evidence;
  const spans = evidence?.spans ?? [];
  const omissions = evidence?.omissions ?? [];
  const changes = omissions.filter(row => row.changed === true).length;
  return <aside ref={panelRef} className="evidence-panel" role={isModal ? 'dialog' : undefined} aria-modal={isModal || undefined} aria-label="Evidence audit"><div className="panel-header"><div><span className="eyebrow">INSPECT THE RECORD</span><h2>Evidence audit</h2></div><button className="icon-button" aria-label="Close evidence audit" onClick={onClose}><X size={19} /></button></div><div className="panel-content">
    {!result && <div className="panel-empty"><SlidersHorizontal size={28} /><h3>Evidence stays with the case</h3><p>Run a diagnostic case to inspect its findings, omission tests and recorded model decision.</p></div>}
    {result && <>
      <section className="audit-section"><h3>Recorded decision</h3><div className="audit-value">{evidence?.decision?.label || 'No valid label'} {evidence?.decision?.name ? `· ${evidence.decision.name}` : ''}</div><p className="review-note">Omission tests describe model behavior. They do not establish clinical causation.</p><div className="metric-grid"><div className="metric-card"><strong>{omissions.length}<small> / {spans.length}</small></strong><span>Spans tested</span></div><div className="metric-card"><strong>{changes}</strong><span>Answer changes</span></div></div></section>
      <section className="audit-section"><h3>Case findings</h3><p className="audit-label">Stable references to the frozen input</p>{spans.length ? spans.map(span => <div id={`span-${span.id}`} key={span.id} className={`evidence-span ${highlight === span.id ? 'evidence-highlight' : ''}`}><span className="mono">{span.id}</span><p>{span.text}</p><span className="audit-label">{span.start != null && span.end != null ? `Characters ${span.start}–${span.end}` : 'Source case span'}</span></div>) : <p className="audit-label">No spans recorded.</p>}</section>
      <section className="audit-section"><h3>Actual omission outcomes</h3>{omissions.length ? omissions.map((row, index) => <div className="omission-row" key={`${row.span_id}-${index}`}><div><a className="jump-link mono" href={`#span-${row.span_id}`} onClick={event => { event.preventDefault(); document.getElementById(`span-${row.span_id}`)?.scrollIntoView({ block: 'center', behavior: 'auto' }); }}>{row.span_id}</a><span>{row.label ? `→ ${row.label}` : 'No valid label'}</span><span className={`status-pill ${row.changed ? 'attention' : ''}`}>{row.changed === true ? 'Changed' : row.changed === false ? 'Unchanged' : 'Unresolved'}</span></div><details><summary>Recorded outcome</summary><pre className="code-block">{pretty(row)}</pre></details></div>) : <p className="audit-label">No omission outcomes recorded.</p>}</section>
      <section className="audit-section"><h3>Selected test and recheck</h3><details open><summary>Selected omission</summary><pre className="code-block">{pretty(evidence?.selected)}</pre></details><details open><summary>Recheck status</summary><pre className="code-block">{pretty(evidence?.recheck)}</pre></details></section>
      <section className="audit-section"><h3>Explanation checks</h3><dl><dt>Output</dt><dd>{readable(result.release_status)}</dd><dt>Automated release passed</dt><dd>{readable(result.automated_release_passed)}</dd></dl><details><summary>Checker record</summary><pre className="code-block">{pretty(result.checker)}</pre></details><p className="audit-label">Checker thresholds are provisional development settings, not a clinical validation claim.</p></section>
      <section className="audit-section"><h3>Model provenance and runtime</h3><details><summary>Target model</summary><pre className="code-block">{pretty(evidence?.target ?? runtime?.target)}</pre></details><details><summary>Communicator</summary><pre className="code-block">{pretty(runtime?.communicator)}</pre></details><details><summary>Time and memory</summary><pre className="code-block">{pretty({ time: result.time, memory: result.memory })}</pre></details><details><summary>Complete analysis record</summary><pre className="code-block">{pretty(result)}</pre></details></section>
    </>}
    <section className="audit-section"><h3>Local service</h3><div className="runtime-line"><span className={`status-dot ${runtime?.ready ? 'ready' : ''}`} />{runtime?.ready ? 'Runtime ready' : runtime?.phase ? readable(runtime.phase) : 'Connecting to runtime'}</div><details><summary>Runtime record</summary><pre className="code-block">{pretty(runtime)}</pre></details></section>
  </div></aside>;
}

export default function App() {
  const [history, setHistory] = useState<CaseSummary[]>([]);
  const [item, setItem] = useState<ClinicalCase | null>(null);
  const [examples, setExamples] = useState<Example[]>([]);
  const [runtime, setRuntime] = useState<Runtime | null>(null);
  const [online, setOnline] = useState(true);
  const [initializing, setInitializing] = useState(true);
  const [mode, setMode] = useState<Mode>('diagnostic');
  const [draft, setDraft] = useState('');
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const [options, setOptions] = useState<Options>({ ...EMPTY_OPTIONS });
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [parentId, setParentId] = useState<string | undefined>();
  const [sourceId, setSourceId] = useState<string | undefined>();
  const [draftTitle, setDraftTitle] = useState<string | undefined>();
  const [sending, setSending] = useState(false);
  const [loadingCase, setLoadingCase] = useState(false);
  const [search, setSearch] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [auditOpen, setAuditOpen] = useState(false);
  const [highlight, setHighlight] = useState<string | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [source, setSource] = useState<Source | null>(null);
  const [modal, setModal] = useState<'sources' | 'about' | 'delete' | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<CaseSummary | null>(null);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>(() => { const saved = localStorage.getItem('trustxai-theme'); return saved === 'light' || saved === 'dark' ? saved : 'system'; });
  const fileRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const navigationRef = useRef(0);
  const sidebarRef = useRef<HTMLElement>(null);
  const sidebarIsModal = useDrawerFocus(sidebarOpen, sidebarRef, '(max-width: 680px)', ['.workspace', '.evidence-panel']);
  const busy = isBusy(item);

  const refreshHistory = useCallback(async () => { const data = await api<CaseSummary[]>('/cases'); setHistory(data); }, []);
  const selectCase = useCallback(async (id: string) => {
    const request = ++navigationRef.current;
    setLoadingCase(true); setError(''); setSidebarOpen(false);
    try { const loaded = await api<ClinicalCase>(`/cases/${encodeURIComponent(id)}`); if (navigationRef.current === request) { setItem(loaded); setDraft(''); setParentId(undefined); setSourceId(undefined); setAuditOpen(false); window.history.replaceState(null, '', `?case=${encodeURIComponent(id)}`); } }
    catch (err) { if (navigationRef.current === request) setError(errorText(err)); }
    finally { if (navigationRef.current === request) setLoadingCase(false); }
  }, []);

  useEffect(() => {
    let mounted = true;
    Promise.allSettled([api<CaseSummary[]>('/cases'), api<Example[]>('/examples'), api<Runtime>('/runtime'), api<Source[]>('/sources')]).then(results => {
      if (!mounted) return;
      const [casesResult, examplesResult, runtimeResult, sourcesResult] = results;
      if (casesResult.status === 'fulfilled') setHistory(casesResult.value); else { setOnline(false); setError('The local service is unavailable. Start the backend, then use Retry connection.'); }
      if (examplesResult.status === 'fulfilled') setExamples(examplesResult.value);
      if (runtimeResult.status === 'fulfilled') setRuntime(runtimeResult.value);
      if (sourcesResult.status === 'fulfilled') setSources(sourcesResult.value);
      setInitializing(false);
      const id = new URLSearchParams(location.search).get('case'); if (id && casesResult.status === 'fulfilled') void selectCase(id);
    });
    return () => { mounted = false; };
  }, [selectCase]);

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const apply = () => { const resolved = theme === 'system' ? media.matches ? 'dark' : 'light' : theme; document.documentElement.dataset.theme = resolved; document.documentElement.style.colorScheme = resolved; };
    apply(); localStorage.setItem('trustxai-theme', theme); media.addEventListener('change', apply);
    return () => media.removeEventListener('change', apply);
  }, [theme]);

  useEffect(() => {
    if (!busy || !item) return;
    let stopped = false;
    const request = navigationRef.current;
    const interval = setInterval(async () => {
      try { const updated = await api<ClinicalCase>(`/cases/${encodeURIComponent(item.id)}`); if (!stopped && request === navigationRef.current) { setItem(updated); setOnline(true); if (!isBusy(updated)) void refreshHistory(); } }
      catch { if (!stopped) setOnline(false); }
    }, 1800);
    return () => { stopped = true; clearInterval(interval); };
  }, [item?.id, busy, refreshHistory]);

  useEffect(() => { const interval = setInterval(() => { api<Runtime>('/runtime').then(value => { setRuntime(value); setOnline(true); }).catch(() => setOnline(false)); }, 12000); return () => clearInterval(interval); }, []);
  useEffect(() => { if (item) endRef.current?.scrollIntoView({ behavior: 'auto', block: 'end' }); }, [item?.id, item?.messages?.length, item?.status]);
  useEffect(() => { if (!notice) return; const timeout = setTimeout(() => setNotice(''), 4000); return () => clearTimeout(timeout); }, [notice]);
  useEffect(() => { const escape = (event: KeyboardEvent) => { if (event.key === 'Escape') { setSidebarOpen(false); setAuditOpen(false); } }; window.addEventListener('keydown', escape); return () => window.removeEventListener('keydown', escape); }, []);

  function newCase(nextMode: Mode = 'diagnostic') {
    ++navigationRef.current; setLoadingCase(false); setItem(null); setMode(nextMode); setDraft(''); setQuestion(DEFAULT_QUESTION); setOptions({ ...EMPTY_OPTIONS }); setDetailsOpen(false); setParentId(undefined); setSourceId(undefined); setDraftTitle(undefined); setError(''); setSidebarOpen(false); setAuditOpen(false); window.history.replaceState(null, '', window.location.pathname); textareaRef.current?.focus();
  }

  function populate(input: CaseInput, title?: string, parent?: string) {
    ++navigationRef.current; setLoadingCase(false); setItem(null); setMode('diagnostic'); setDraft(input.case_text || ''); setQuestion(input.question || DEFAULT_QUESTION); setOptions({ ...EMPTY_OPTIONS, ...input.options }); setDetailsOpen(true); setParentId(parent); setSourceId(input.source_id); setDraftTitle(title); setError(''); setAuditOpen(false); window.history.replaceState(null, '', window.location.pathname); textareaRef.current?.focus();
  }

  async function submit(event: FormEvent) {
    event.preventDefault(); if (sending || busy || !draft.trim()) return;
    if (!item && mode === 'diagnostic' && (!question.trim() || OPTION_KEYS.some(key => !options[key].trim()))) { setDetailsOpen(true); setError('Add the diagnostic question and all four candidate diagnoses.'); return; }
    setSending(true); setError(''); const request = navigationRef.current;
    try {
      const path = item ? `/cases/${encodeURIComponent(item.id)}/messages` : mode === 'chat' ? '/chats' : '/cases';
      const body = item || mode === 'chat' ? { text: draft.trim() } : { case_text: draft.trim(), question: question.trim(), options: Object.fromEntries(OPTION_KEYS.map(key => [key, options[key].trim()])), parent_id: parentId, source_id: sourceId, title: draftTitle };
      const created = await api<ClinicalCase>(path, jsonBody(body));
      if (request === navigationRef.current) { setItem(created); setDraft(''); setParentId(undefined); window.history.replaceState(null, '', `?case=${encodeURIComponent(created.id)}`); }
      await refreshHistory();
    } catch (err) { setError(errorText(err)); } finally { setSending(false); }
  }

  async function cancel() {
    if (!item) return; const id = item.id; const request = navigationRef.current;
    try { const updated = await api<ClinicalCase>(`/cases/${encodeURIComponent(id)}/cancel`, { method: 'POST' }); if (request === navigationRef.current) setItem(updated); await refreshHistory(); } catch (err) { setError(errorText(err)); }
  }

  async function removeCase() {
    if (!deleteTarget) return; setSending(true);
    try { await api(`/cases/${encodeURIComponent(deleteTarget.id)}`, { method: 'DELETE' }); if (item?.id === deleteTarget.id) newCase(); await refreshHistory(); setModal(null); setDeleteTarget(null); setNotice('Conversation deleted.'); } catch (err) { setError(errorText(err)); } finally { setSending(false); }
  }

  async function copy(text: string) {
    try { await navigator.clipboard.writeText(text); setNotice('Copied to clipboard.'); } catch { setError('Clipboard access is unavailable in this browser.'); }
  }

  async function importFile(file?: File) {
    if (!file) return;
    if (file.size > 1024 * 1024) { setError('Choose a text or JSON file smaller than 1 MB.'); return; }
    try {
      const text = await file.text();
      if (file.name.toLowerCase().endsWith('.json') || text.trimStart().startsWith('{')) {
        const parsed = JSON.parse(text); const input = parsed.input ?? parsed;
        if (typeof input.case_text !== 'string') throw new Error('The JSON needs a case_text field, and can include question, options and title.');
        if (input.options && (typeof input.options !== 'object' || OPTION_KEYS.some(key => input.options[key] != null && typeof input.options[key] !== 'string'))) throw new Error('Each candidate diagnosis must be text under option A, B, C or D.');
        populate({ ...input, kind: 'diagnostic' }, parsed.title || input.title || file.name.replace(/\.[^.]+$/, '')); setNotice('Case imported. Review it before running.');
      } else {
        const importedOptions = { ...EMPTY_OPTIONS }; const lines = text.split('\n'); const caseLines: string[] = [];
        for (const line of lines) { const match = line.match(/^\s*([A-D])[.):]\s+(.+)$/); if (match) importedOptions[match[1] as keyof Options] = match[2]; else caseLines.push(line); }
        let importedQuestion = DEFAULT_QUESTION; const last = caseLines.map(line => line.trim().endsWith('?')).lastIndexOf(true); if (last >= 0) importedQuestion = caseLines.splice(last, 1)[0].trim();
        populate({ kind: 'diagnostic', case_text: caseLines.join('\n').trim(), question: importedQuestion, options: importedOptions }, file.name.replace(/\.[^.]+$/, '')); setNotice('Text imported. Review the question and four options.');
      }
    } catch (err) { setError(`Could not import this file. ${errorText(err)}`); }
    finally { if (fileRef.current) fileRef.current.value = ''; }
  }

  async function reconnect() {
    setError('');
    try { const [cases, state, available, library] = await Promise.all([api<CaseSummary[]>('/cases'), api<Runtime>('/runtime'), api<Example[]>('/examples'), api<Source[]>('/sources')]); setHistory(cases); setRuntime(state); setExamples(available); setSources(library); setOnline(true); setNotice('Connected to the local service.'); } catch (err) { setOnline(false); setError(errorText(err)); }
  }

  function inspectOmission() {
    const selected = item?.result?.evidence.selected;
    const span = selected && typeof selected === 'object' && 'span_id' in selected ? String(selected.span_id) : item?.result?.evidence.omissions?.[0]?.span_id;
    setHighlight(span || null); setAuditOpen(true);
    if (span) setTimeout(() => document.getElementById(`span-${span}`)?.scrollIntoView({ behavior: 'auto', block: 'center' }), 50);
  }

  const filteredHistory = history.filter(row => row.title.toLowerCase().includes(search.toLowerCase()));
  const userMessages = item?.messages?.filter(message => message.role === 'user') ?? [];
  const hasAnalysisMessage = item?.messages?.some(message => message.kind === 'analysis');
  const currentMode = item ? item.input.kind : mode;
  const matchedExample = item?.input.kind === 'diagnostic' ? examples.find(example => example.case_text === item.input.case_text && example.question === item.input.question && OPTION_KEYS.every(key => example.options?.[key] === item.input.options?.[key])) : undefined;
  const caseOrigin = matchedExample ? matchedExample.synthetic ? 'Synthetic research case' : 'Public MedQA case' : undefined;
  const diagnosticDraft = !item && mode === 'diagnostic';
  let analysisShown = false;

  return <div className={`app-shell ${auditOpen ? 'evidence-open' : ''}`}>
    <a href="#composer-input" className="skip-link">Skip to message composer</a>
    {sidebarOpen && <button className="mobile-backdrop" aria-label="Close sidebar" onClick={() => setSidebarOpen(false)} />}
    <aside ref={sidebarRef} className={`sidebar ${sidebarOpen ? 'is-open' : ''}`} role={sidebarIsModal ? 'dialog' : undefined} aria-modal={sidebarIsModal || undefined} aria-label="Conversation navigation"><div className="sidebar-top"><a className="brand" href="/" onClick={event => { event.preventDefault(); newCase(); }}><Mark /><span><span className="brand-word">TRUSTXAI</span><span className="brand-subtitle">Clinical workspace</span></span></a><button className="icon-button mobile-menu" aria-label="Close navigation" onClick={() => setSidebarOpen(false)}><PanelLeftClose size={18} /></button></div>
      <button className="new-case" onClick={() => newCase()}><Plus size={18} /> New conversation</button>
      <label className="search-box"><Search size={15} /><span className="visually-hidden">Search conversations</span><input placeholder="Search conversations" value={search} onChange={event => setSearch(event.target.value)} /></label>
      <div className="section-heading">Your conversations<span>{history.length || ''}</span></div>
      <nav className="history-list" aria-label="Saved conversations">{initializing ? <div className="history-empty">Connecting to local service…</div> : filteredHistory.length ? filteredHistory.map(row => <div className={`history-item ${item?.id === row.id ? 'active' : ''}`} key={row.id}><button className="history-main" onClick={() => void selectCase(row.id)} aria-current={item?.id === row.id ? 'page' : undefined}><MessageSquare size={15} /><span>{row.title}</span>{['running', 'queued', 'cancelling'].includes(row.status) && <LoaderCircle size={13} className="loading-spinner" aria-label={row.status} />}</button><button className="history-actions icon-button" aria-label={`Delete ${row.title}`} onClick={() => { setDeleteTarget(row); setModal('delete'); }}><Trash2 size={14} /></button></div>) : <div className="history-empty">{search ? 'No matching conversations.' : 'Your cases and questions will appear here.'}</div>}</nav>
      <div className="sidebar-bottom"><button className="text-button" onClick={() => setModal('sources')}><BookOpen size={17} />Source library<span>{sources.length}</span></button><button className="text-button" onClick={() => setModal('about')}><CircleHelp size={17} />About this workspace</button><div className="theme-switch" role="group" aria-label="Color theme">{([{ key: 'light', label: 'Light theme', icon: Sun }, { key: 'dark', label: 'Dark theme', icon: Moon }, { key: 'system', label: 'System theme', icon: Monitor }] as const).map(({ key, label, icon: Icon }) => <button key={key} className={theme === key ? 'active' : ''} onClick={() => setTheme(key)} aria-label={label} aria-pressed={theme === key}><Icon size={16} /></button>)}</div><div className="sidebar-footnote"><span className="status-dot" />Local research prototype</div></div>
    </aside>

    <main className="workspace"><header className="topbar"><div className="breadcrumb"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><span>{item?.title || (parentId ? 'New case version' : 'New conversation')}</span><ChevronDown size={14} /></div><div className="topbar-actions"><button className="runtime-status text-button" onClick={() => setModal('about')} title="Local runtime status"><span className={`status-dot ${online && runtime?.ready ? 'ready' : ''}`} />{!online ? 'Offline' : runtime?.ready ? 'Local runtime' : 'Preparing runtime'}</button><span className="prototype-badge">{caseOrigin || 'Research preview'}</span>{item && <a className="icon-button" href={`/api/cases/${encodeURIComponent(item.id)}/export`} download aria-label="Export conversation as JSON" title="Export JSON"><Download size={17} /></a>}<button className={`icon-button ${auditOpen ? 'selected' : ''}`} aria-label={auditOpen ? 'Close evidence audit' : 'Open evidence audit'} aria-expanded={auditOpen} onClick={() => setAuditOpen(!auditOpen)} title="Evidence audit"><PanelRight size={19} /></button></div></header>

      <div className="conversation" aria-label="Conversation">{loadingCase ? <div className="empty-state"><LoaderCircle className="loading-spinner" size={24} /><p>Opening conversation…</p></div> : !item ? <div className="welcome"><div className="welcome-mark"><Mark /></div><div className="eyebrow">A CLEARER VIEW OF THE EVIDENCE</div><h1 className="welcome-title">Reason through a case.<br />Keep the evidence in view.</h1><p className="welcome-copy">Explore a diagnostic question or ask with sources.<br />Your local research workspace, with the record attached.</p><div className="mode-tabs" role="group" aria-label="Conversation type"><button className={`mode-tab ${mode === 'diagnostic' ? 'active' : ''}`} aria-pressed={mode === 'diagnostic'} onClick={() => setMode('diagnostic')}><Activity size={16} />Diagnostic case</button><button className={`mode-tab ${mode === 'chat' ? 'active' : ''}`} aria-pressed={mode === 'chat'} onClick={() => setMode('chat')}><MessageSquare size={16} />Ask with sources</button></div>
        {mode === 'diagnostic' ? <><p className="welcome-note">Enter a vignette and four candidate diagnoses, or select a research case.</p><div className="example-grid">{examples.map((example, index) => <button className="example-card" key={example.id} onClick={() => populate({ ...example, source_id: example.source_id || example.id }, example.title)}><span className="example-label"><FileText size={14} />{example.synthetic ? 'SYNTHETIC CASE' : 'PUBLIC MEDQA CASE'} {String(index + 1).padStart(2, '0')}</span><strong>{example.title}</strong><span>Review case<ChevronRight size={14} /></span></button>)}</div>{!examples.length && !initializing && <p className="welcome-note">Type your vignette below to begin.</p>}</> : <div className="ask-intro"><BookOpen size={21} /><div><h2>Answers with a source trail</h2><p>Ask about public datasets, this research framework or a recorded case audit. Open each cited source note to inspect its support.</p><button className="text-button" onClick={() => setModal('sources')}>Browse the source library <ChevronRight size={14} /></button></div></div>}
      </div> : <div className="messages">{(item.messages || []).map(message => {
        if (message.kind === 'analysis') { if (analysisShown || !item.result) return null; analysisShown = true; return <article className="message message-assistant" key={message.id}><div className="message-avatar"><Mark small /></div><div className="message-content"><div className="message-label">TRUSTXAI<span>Diagnostic analysis</span></div><ResultCard result={item.result} onAudit={() => setAuditOpen(true)} onCopy={copy} /><div className="message-actions"><button className="text-button" onClick={inspectOmission}><Search size={14} />Inspect an omitted finding</button></div></div></article>; }
        return <article className={`message message-${message.role}`} key={message.id}>{message.role === 'assistant' && <div className="message-avatar"><Mark small /></div>}<div className="message-content"><div className="message-label">{message.role === 'user' ? 'You' : 'TRUSTXAI'}{message.role === 'assistant' && <span>With recorded sources</span>}</div>{message.role === 'user' ? message.kind === 'case' || (userMessages[0]?.id === message.id && item.input.kind === 'diagnostic') ? <UserInput input={item.input} onEdit={() => populate(item.input, `${item.title} · revised`, item.id)} /> : <p className="message-bubble">{message.payload.text || message.payload.case_text}</p> : <Answer message={message} onSource={setSource} />}</div></article>;
      })}{!item.messages?.length && <article className="message message-user"><div className="message-content"><div className="message-label">You</div><UserInput input={item.input} onEdit={() => populate(item.input, `${item.title} · revised`, item.id)} /></div></article>}{item.result && !hasAnalysisMessage && <article className="message message-assistant"><div className="message-avatar"><Mark small /></div><div className="message-content"><div className="message-label">TRUSTXAI</div><ResultCard result={item.result} onAudit={() => setAuditOpen(true)} onCopy={copy} /><button className="text-button" onClick={inspectOmission}><Search size={14} />Inspect an omitted finding</button></div></article>}
        {busy && <div className="progress-card" role="status" aria-live="polite"><div className="progress-header"><LoaderCircle size={17} className="loading-spinner" /><strong>{item.status === 'cancelling' ? 'Stopping this run' : item.status === 'queued' ? 'Waiting for the local runtime' : readable(item.progress?.stage || 'Analyzing')}</strong><span>{item.progress?.percent != null ? `${Math.round(item.progress.percent)}%` : ''}</span></div><p className="progress-detail">{item.progress?.detail || 'The recorded result will appear when processing completes.'}</p>{item.progress?.percent != null && <div className="progress-track"><div className="progress-fill" style={{ width: `${Math.max(0, Math.min(100, item.progress.percent))}%` }} /></div>}<button className="text-button" disabled={item.status === 'cancelling'} onClick={() => void cancel()}><Square size={12} />{item.status === 'cancelling' ? 'Cancellation requested' : 'Stop processing'}</button></div>}
        {item.status === 'failed' && <div className="error-card" role="alert"><strong>This request could not finish.</strong><p>{typeof item.error === 'object' && item.error && 'message' in item.error ? String(item.error.message) : readable(item.error || 'No error detail was recorded.')}</p>{item.input.kind === 'diagnostic' && <button className="text-button" onClick={() => populate(item.input, item.title, item.id)}><Pencil size={14} />Review and try as a new case</button>}</div>}{item.status === 'cancelled' && <div className="review-note">Processing was cancelled. Any completed evidence remains in this record.</div>}
      </div>}<div ref={endRef} /></div>

      <div className="composer-region"><div className="composer-container">{error && <div className="inline-error" role="alert"><span>{error}</span>{!online && <button className="text-button" onClick={() => void reconnect()}>Retry connection</button>}<button className="icon-button" aria-label="Dismiss error" onClick={() => setError('')}><X size={15} /></button></div>}{parentId && <div className="composer-context"><Pencil size={14} />New version · The previous case stays in history.</div>}
        <form className="composer" onSubmit={submit}><div className="composer-header"><span className="mode-label">{item ? <><MessageSquare size={14} />Follow up on this conversation</> : currentMode === 'diagnostic' ? <><Activity size={14} />Diagnostic case</> : <><BookOpen size={14} />Ask with sources</>}</span>{diagnosticDraft && <button type="button" className="options-toggle" onClick={() => setDetailsOpen(!detailsOpen)} aria-expanded={detailsOpen} aria-controls="candidate-fields">Question & 4 options <ChevronDown size={14} /></button>}</div><label className="visually-hidden" htmlFor="composer-input">{item ? 'Follow-up question' : mode === 'diagnostic' ? 'Clinical vignette' : 'Your question'}</label><textarea ref={textareaRef} id="composer-input" className="composer-textarea" placeholder={item ? 'Ask about this case or its recorded evidence…' : mode === 'diagnostic' ? 'Describe the clinical vignette…' : 'Ask a question to explore with sources…'} rows={diagnosticDraft && detailsOpen ? 3 : 3} value={draft} onChange={event => { setDraft(event.target.value); if (!item) setSourceId(undefined); }} disabled={sending} onKeyDown={event => { if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
          {diagnosticDraft && detailsOpen && <div className="composer-details" id="candidate-fields"><label className="field"><span className="field-label">Diagnostic question</span><input value={question} onChange={event => { setQuestion(event.target.value); setSourceId(undefined); }} placeholder={DEFAULT_QUESTION} /></label><div className="options-grid">{OPTION_KEYS.map(key => <label className="field option-field" key={key}><span className="field-label">{key}</span><input aria-label={`Candidate diagnosis ${key}`} placeholder={`Candidate diagnosis ${key}`} value={options[key]} onChange={event => { setOptions(previous => ({ ...previous, [key]: event.target.value })); setSourceId(undefined); }} /></label>)}</div></div>}
          <div className="composer-footer"><div className="composer-tools">{!item && <><button type="button" className="icon-button" title="Import text or JSON case" aria-label="Import text or JSON case" onClick={() => fileRef.current?.click()}><Upload size={18} /></button><span className="attachment-label">Text or JSON</span><input type="file" accept=".txt,.json,text/plain,application/json" className="visually-hidden" ref={fileRef} onChange={event => void importFile(event.target.files?.[0])} /></>}{item && <button type="button" className="text-button" onClick={() => setModal('sources')}><BookOpen size={15} />Sources</button>}</div><div className="composer-actions">{!item && mode === 'diagnostic' && <span className="composer-hint">{OPTION_KEYS.filter(key => options[key].trim()).length}/4 options</span>}{busy ? <button type="button" className="send-button stop" aria-label="Stop processing" onClick={() => void cancel()} disabled={item?.status === 'cancelling'}><Square size={15} fill="currentColor" /></button> : <button type="submit" className="send-button" aria-label={item ? 'Send follow-up question' : mode === 'diagnostic' ? 'Analyze diagnostic case' : 'Send question'} disabled={sending || loadingCase || !draft.trim()}>{sending ? <LoaderCircle size={19} className="loading-spinner" /> : <ArrowUp size={21} />}</button>}</div></div>
        </form><p className="composer-disclaimer">Research prototype. Review all model suggestions and sources. {diagnosticDraft ? 'Selects among your four supplied options.' : 'Not a substitute for clinical judgment.'}</p>
      </div></div>
    </main>
    {auditOpen && <><button className="evidence-backdrop" aria-label="Close evidence drawer" onClick={() => setAuditOpen(false)} /><EvidencePanel item={item} runtime={runtime} onClose={() => setAuditOpen(false)} highlight={highlight} /></>}
    {notice && <div className="toast" role="status"><Check size={16} />{notice}</div>}
    {source && <Dialog title="Source passage" onClose={() => setSource(null)}><SourceDetails source={source} /></Dialog>}
    {modal === 'sources' && <Dialog title="Source library" onClose={() => setModal(null)}><p className="modal-intro">Answers can draw on these recorded sources. Inspect the cited passage alongside each answer.</p><div className="source-list">{sources.length ? sources.map((record, index) => <SourceDetails source={record} key={record.id || index} />) : <p>No sources are available from the local service.</p>}</div></Dialog>}
    {modal === 'about' && <Dialog title="About this workspace" onClose={() => setModal(null)}><div className="about-brand"><Mark /><h3>TRUSTXAI</h3><span className="prototype-badge">Research preview</span></div><p>A local clinical decision-support research prototype. Diagnostic analysis selects one of four supplied options and records what happens when individual case findings are omitted.</p><p>Ask-with-sources uses the recorded source library. Source support and automated explanation checks do not establish clinical accuracy.</p><div className="check-row"><span className={`status-dot ${online && runtime?.ready ? 'ready' : ''}`} /><strong>{!online ? 'Local service unavailable' : runtime?.ready ? 'Local runtime ready' : 'Runtime preparation in progress'}</strong></div><details><summary>Runtime and model details</summary><pre className="code-block">{pretty(runtime)}</pre></details><p className="audit-label">Explanations, audit details and exports stay attached to each frozen case. Editing creates a new case version.</p></Dialog>}
    {modal === 'delete' && deleteTarget && <Dialog title="Delete this conversation?" onClose={() => setModal(null)} footer={<><button className="button button-secondary" onClick={() => setModal(null)}>Keep conversation</button><button className="button button-danger" disabled={sending} onClick={() => void removeCase()}>{sending ? 'Deleting…' : 'Delete conversation'}</button></>}><p>“{deleteTarget.title}” will be removed from your conversation history.</p></Dialog>}
  </div>;
}
