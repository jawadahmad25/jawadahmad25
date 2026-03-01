import { useState, useEffect } from 'react';
import { FileText, Plus, Table, Sparkles, BookMarked, Copy, Check } from 'lucide-react';
import { listPublications, createPublication, generateLatexTable, generateHighlights, addCitation } from '../services/api';
import type { Publication, LatexTableResponse, HighlightsResponse } from '../types';

type Tab = 'papers' | 'latex' | 'highlights' | 'citations';

export default function PublicationsPage() {
  const [tab, setTab] = useState<Tab>('papers');
  const [publications, setPublications] = useState<Publication[]>([]);
  const [showNewPub, setShowNewPub] = useState(false);

  // New publication form
  const [pubTitle, setPubTitle] = useState('');
  const [pubJournal, setPubJournal] = useState('');
  const [pubAbstract, setPubAbstract] = useState('');

  // LaTeX table
  const [csvText, setCsvText] = useState('');
  const [tableCaption, setTableCaption] = useState('Comparison Results');
  const [tableLabel, setTableLabel] = useState('tab:results');
  const [fontSize, setFontSize] = useState('normalsize');
  const [latexResult, setLatexResult] = useState<LatexTableResponse | null>(null);

  // Highlights
  const [hlAbstract, setHlAbstract] = useState('');
  const [hlResult, setHlResult] = useState<HighlightsResponse | null>(null);

  // Citations
  const [bibtex, setBibtex] = useState('');
  const [citationResult, setCitationResult] = useState<{ formatted_ieee: string; formatted_elsevier: string } | null>(null);

  const [copied, setCopied] = useState(false);

  useEffect(() => {
    listPublications().then(setPublications).catch(console.error);
  }, []);

  const handleCreatePub = async () => {
    if (!pubTitle) return;
    await createPublication({ title: pubTitle, journal: pubJournal, abstract: pubAbstract });
    const pubs = await listPublications();
    setPublications(pubs);
    setShowNewPub(false);
    setPubTitle('');
    setPubJournal('');
    setPubAbstract('');
  };

  const handleGenerateTable = async () => {
    if (!csvText) return;
    const result = await generateLatexTable({
      csv_text: csvText,
      caption: tableCaption,
      label: tableLabel,
      font_size: fontSize,
    });
    setLatexResult(result);
  };

  const handleGenerateHighlights = async () => {
    if (!hlAbstract) return;
    const result = await generateHighlights({ abstract: hlAbstract });
    setHlResult(result);
  };

  const handleAddCitation = async () => {
    if (!bibtex) return;
    const result = await addCitation({ bibtex });
    setCitationResult(result);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs: { id: Tab; label: string; icon: typeof FileText }[] = [
    { id: 'papers', label: 'Papers', icon: FileText },
    { id: 'latex', label: 'LaTeX Tables', icon: Table },
    { id: 'highlights', label: 'Highlights', icon: Sparkles },
    { id: 'citations', label: 'Citations', icon: BookMarked },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Publications</h1>
        <p className="text-sm text-surface-500 mt-1">Paper management, LaTeX tools, and citation formatting</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-100 dark:bg-surface-800 p-1 rounded-lg w-fit">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.id
                ? 'bg-white dark:bg-surface-700 text-surface-900 dark:text-white shadow-sm'
                : 'text-surface-500 hover:text-surface-700'
            }`}
          >
            <t.icon size={16} />
            {t.label}
          </button>
        ))}
      </div>

      {/* Papers Tab */}
      {tab === 'papers' && (
        <div className="space-y-4">
          <button onClick={() => setShowNewPub(!showNewPub)} className="btn-primary flex items-center gap-2">
            <Plus size={16} /> New Publication
          </button>

          {showNewPub && (
            <div className="card p-5 space-y-4">
              <div>
                <label className="label">Title *</label>
                <input className="input-field" value={pubTitle} onChange={e => setPubTitle(e.target.value)} placeholder="Paper title" />
              </div>
              <div>
                <label className="label">Journal</label>
                <input className="input-field" value={pubJournal} onChange={e => setPubJournal(e.target.value)} placeholder="e.g., IEEE TAP" />
              </div>
              <div>
                <label className="label">Abstract</label>
                <textarea className="input-field h-24" value={pubAbstract} onChange={e => setPubAbstract(e.target.value)} placeholder="Paper abstract..." />
              </div>
              <button onClick={handleCreatePub} className="btn-primary">Create</button>
            </div>
          )}

          <div className="card">
            {publications.length === 0 ? (
              <div className="p-8 text-center text-surface-400">
                <FileText className="mx-auto mb-2" size={24} />
                <p className="text-sm">No publications yet.</p>
              </div>
            ) : (
              <div className="divide-y divide-surface-100 dark:divide-surface-800">
                {publications.map(p => (
                  <div key={p.id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-surface-900 dark:text-white">{p.title}</p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-surface-400">
                          {p.journal && <span>{p.journal}</span>}
                          <span className="px-2 py-0.5 bg-surface-100 dark:bg-surface-700 rounded-full">{p.status}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* LaTeX Table Tab */}
      {tab === 'latex' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-5 space-y-4">
            <h3 className="font-semibold text-surface-900 dark:text-white">Input Data (CSV)</h3>
            <textarea
              className="input-field h-48 font-mono text-xs"
              value={csvText}
              onChange={e => setCsvText(e.target.value)}
              placeholder="Model,MSE,RMSE,R2&#10;Linear Regression,0.0045,0.0671,0.8923&#10;Random Forest,0.0012,0.0346,0.9712"
            />
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Caption</label>
                <input className="input-field" value={tableCaption} onChange={e => setTableCaption(e.target.value)} />
              </div>
              <div>
                <label className="label">Label</label>
                <input className="input-field" value={tableLabel} onChange={e => setTableLabel(e.target.value)} />
              </div>
            </div>
            <div>
              <label className="label">Font Size</label>
              <select className="input-field" value={fontSize} onChange={e => setFontSize(e.target.value)}>
                <option value="normalsize">Normal</option>
                <option value="small">Small</option>
                <option value="footnotesize">Footnotesize</option>
                <option value="scriptsize">Scriptsize</option>
              </select>
            </div>
            <button onClick={handleGenerateTable} className="btn-primary w-full">Generate LaTeX Table</button>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-surface-900 dark:text-white">LaTeX Output</h3>
              {latexResult && (
                <button onClick={() => copyToClipboard(latexResult.latex_code)} className="btn-secondary flex items-center gap-1 text-xs">
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              )}
            </div>
            {latexResult ? (
              <pre className="bg-surface-50 dark:bg-surface-900 p-4 rounded-lg text-xs font-mono overflow-x-auto whitespace-pre">
                {latexResult.latex_code}
              </pre>
            ) : (
              <div className="flex items-center justify-center h-48 bg-surface-50 dark:bg-surface-800 rounded-lg text-surface-400 text-sm">
                Paste CSV data and click Generate
              </div>
            )}
          </div>
        </div>
      )}

      {/* Highlights Tab */}
      {tab === 'highlights' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-5 space-y-4">
            <h3 className="font-semibold text-surface-900 dark:text-white">Paper Abstract</h3>
            <textarea
              className="input-field h-48"
              value={hlAbstract}
              onChange={e => setHlAbstract(e.target.value)}
              placeholder="Paste your paper abstract here..."
            />
            <button onClick={handleGenerateHighlights} className="btn-primary w-full">
              Generate Highlights
            </button>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-surface-900 dark:text-white">Research Highlights</h3>
              {hlResult && (
                <button onClick={() => copyToClipboard(hlResult.latex_formatted)} className="btn-secondary flex items-center gap-1 text-xs">
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy LaTeX'}
                </button>
              )}
            </div>
            {hlResult ? (
              <div className="space-y-3">
                {hlResult.highlights.map((h, i) => (
                  <div key={i} className="flex gap-2 p-2 bg-surface-50 dark:bg-surface-800 rounded-lg">
                    <span className="text-xs font-bold text-primary-600 mt-0.5">{i + 1}.</span>
                    <p className="text-sm text-surface-700 dark:text-surface-300">{h}</p>
                    <span className="text-xs text-surface-400 whitespace-nowrap">{h.length}/85</span>
                  </div>
                ))}
                <div className="mt-4">
                  <p className="text-xs font-medium text-surface-500 mb-1">LaTeX:</p>
                  <pre className="bg-surface-50 dark:bg-surface-900 p-3 rounded-lg text-xs font-mono overflow-x-auto">
                    {hlResult.latex_formatted}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 bg-surface-50 dark:bg-surface-800 rounded-lg text-surface-400 text-sm">
                Paste abstract and click Generate
              </div>
            )}
          </div>
        </div>
      )}

      {/* Citations Tab */}
      {tab === 'citations' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-5 space-y-4">
            <h3 className="font-semibold text-surface-900 dark:text-white">BibTeX Entry</h3>
            <textarea
              className="input-field h-48 font-mono text-xs"
              value={bibtex}
              onChange={e => setBibtex(e.target.value)}
              placeholder="@article{key,&#10;  author = {Author Name},&#10;  title = {Paper Title},&#10;  journal = {Journal Name},&#10;  year = {2026}&#10;}"
            />
            <button onClick={handleAddCitation} className="btn-primary w-full">Format Citation</button>
          </div>

          <div className="card p-5 space-y-4">
            <h3 className="font-semibold text-surface-900 dark:text-white">Formatted Citations</h3>
            {citationResult ? (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs font-medium text-surface-500">IEEE Style:</p>
                    <button onClick={() => copyToClipboard(citationResult.formatted_ieee)} className="text-xs text-primary-600 hover:text-primary-700">Copy</button>
                  </div>
                  <p className="text-sm bg-surface-50 dark:bg-surface-800 p-3 rounded-lg">{citationResult.formatted_ieee}</p>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs font-medium text-surface-500">Elsevier Style:</p>
                    <button onClick={() => copyToClipboard(citationResult.formatted_elsevier)} className="text-xs text-primary-600 hover:text-primary-700">Copy</button>
                  </div>
                  <p className="text-sm bg-surface-50 dark:bg-surface-800 p-3 rounded-lg">{citationResult.formatted_elsevier}</p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 bg-surface-50 dark:bg-surface-800 rounded-lg text-surface-400 text-sm">
                Paste BibTeX and click Format
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
