import React, { useState } from 'react'
import Dashboard from './Dashboard'

type Page = 'upload' | 'dashboard'

async function uploadPack(file: File) {
  const fd = new FormData();
  fd.append('file', file);
  const res = await fetch('/api/analyze/pack', {
    method: 'POST',
    body: fd
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const data = await uploadPack(file)
      setReport(data.report_markdown)
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Analyse Legal Pack</h2>
      <p>Upload your auction legal pack (PDF/ZIP). Get a Nick-style triage with page-level references.</p>
      <form onSubmit={onSubmit}>
        <input type="file" accept="application/pdf,application/zip" onChange={e => setFile(e.target.files?.[0] || null)} />
        <button type="submit" disabled={!file || loading} style={{ marginLeft: 12 }}>
          {loading ? 'Analysing...' : 'Analyse'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {report && (
        <div style={{ marginTop: 24 }}>
          <h2>Report</h2>
          <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f9fa', padding: 16, borderRadius: 8, overflow: 'auto' }}>{report}</pre>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [page, setPage] = useState<Page>('upload')

  const navStyle = (active: boolean): React.CSSProperties => ({
    padding: '12px 24px',
    background: active ? '#0066cc' : '#e9ecef',
    color: active ? 'white' : '#333',
    border: 'none',
    borderRadius: '8px 8px 0 0',
    cursor: 'pointer',
    fontWeight: active ? 600 : 400,
    fontSize: 15,
    marginRight: 4
  })

  return (
    <div style={{ maxWidth: 1000, margin: '40px auto', fontFamily: 'Inter, system-ui, sans-serif', padding: '0 20px' }}>
      <h1 style={{ marginBottom: 8 }}>PKH Legal Brain</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>AI-powered legal pack analysis for UK property auctions</p>

      {/* Navigation */}
      <nav style={{ marginBottom: 0 }}>
        <button style={navStyle(page === 'upload')} onClick={() => setPage('upload')}>
          Upload & Analyse
        </button>
        <button style={navStyle(page === 'dashboard')} onClick={() => setPage('dashboard')}>
          Rules Dashboard
        </button>
      </nav>

      {/* Content */}
      <div style={{ border: '1px solid #dee2e6', borderRadius: '0 8px 8px 8px', padding: 24, background: 'white' }}>
        {page === 'upload' && <UploadPage />}
        {page === 'dashboard' && <Dashboard />}
      </div>
    </div>
  )
}
