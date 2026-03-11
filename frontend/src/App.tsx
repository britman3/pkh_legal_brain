import React, { useState } from 'react'

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

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<string | null>(null)
  const [analysisId, setAnalysisId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const data = await uploadPack(file)
      setReport(data.report_markdown)
      setAnalysisId(data.analysis_id)
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = () => {
    if (!analysisId) return
    window.open(`/api/analyze/download-pdf/${analysisId}`, '_blank')
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'Inter, system-ui' }}>
      <h1>PKH Legal Brain</h1>
      <p>Upload your auction legal pack (PDF/ZIP). Get a Nick‑style triage with page‑level references.</p>
      
      <form onSubmit={onSubmit}>
        <input 
          type="file" 
          accept="application/pdf,application/zip" 
          onChange={e => setFile(e.target.files?.[0] || null)} 
        />
        <button type="submit" disabled={!file || loading} style={{ marginLeft: 12 }}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {report && (
        <div style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0 }}>Report</h2>
            <button 
              onClick={downloadPDF}
              style={{
                padding: '12px 24px',
                background: '#2c3e50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 500
              }}
            >
              📄 Download PDF Report
            </button>
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: 20, borderRadius: 4 }}>{report}</pre>
        </div>
      )}
    </div>
  )
}
