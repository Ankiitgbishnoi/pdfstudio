import { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const operationConfig = {
  merge: {
    label: 'Merge PDFs',
    description: 'Combine multiple PDF files into one output PDF.',
    acceptsMultiple: true,
    needsPages: false,
    needsText: false,
  },
  split: {
    label: 'Split PDF',
    description: 'Split a PDF into one file per page and download as a ZIP.',
    acceptsMultiple: false,
    needsPages: false,
    needsText: false,
  },
  rotate: {
    label: 'Rotate PDF',
    description: 'Rotate all pages by a specified degree value.',
    acceptsMultiple: false,
    needsPages: false,
    needsText: false,
  },
  extract: {
    label: 'Extract Pages',
    description: 'Extract specific pages from the uploaded PDF.',
    acceptsMultiple: false,
    needsPages: true,
    needsText: false,
  },
  watermark: {
    label: 'Add Watermark',
    description: 'Add a text watermark to each page of a PDF.',
    acceptsMultiple: false,
    needsPages: false,
    needsText: true,
  },
}

function App() {
  const [operation, setOperation] = useState('merge')
  const [files, setFiles] = useState([])
  const [pages, setPages] = useState('1,3-5')
  const [degrees, setDegrees] = useState('90')
  const [watermarkText, setWatermarkText] = useState('CONFIDENTIAL')
  const [status, setStatus] = useState('Ready')
  const [loading, setLoading] = useState(false)

  const config = useMemo(() => operationConfig[operation], [operation])

  const handleFileChange = (event) => {
    const selected = Array.from(event.target.files)
    setFiles(selected)
  }

  const downloadBlob = (blob, fileName) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setStatus('Processing…')

    try {
      if (!files.length) {
        throw new Error('Please upload at least one PDF file.')
      }

      const formData = new FormData()

      if (config.acceptsMultiple) {
        files.forEach((file) => formData.append('files', file))
      } else {
        formData.append('file', files[0])
      }

      if (config.needsPages) {
        formData.append('pages', pages)
      }

      if (operation === 'rotate') {
        formData.append('degrees', degrees)
      }

      if (config.needsText) {
        formData.append('text', watermarkText)
      }

      const response = await fetch(`${API_BASE}/${operation}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Request failed.' }))
        throw new Error(errorData.error || 'Request failed.')
      }

      const blob = await response.blob()
      const fileName = operation === 'split' ? 'split_pages.zip' : `${operation}.pdf`
      downloadBlob(blob, fileName)
      setStatus(`${operationConfig[operation].label} complete.`)
    } catch (error) {
      setStatus(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <div className="panel">
        <h1>pdfstudio web</h1>
        <p className="subtitle">Edit PDFs in your browser</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            PDF Action
            <select value={operation} onChange={(e) => setOperation(e.target.value)}>
              {Object.entries(operationConfig).map(([key, value]) => (
                <option key={key} value={key}>{value.label}</option>
              ))}
            </select>
          </label>

          <div className="info-box">
            <strong>{config.label}</strong>
            <span>{config.description}</span>
          </div>

          <label className="upload-label">
            Select PDF file{config.acceptsMultiple ? 's' : ''}
            <input type="file" accept=".pdf,application/pdf" multiple={config.acceptsMultiple} onChange={handleFileChange} />
          </label>

          {config.needsPages && (
            <label>
              Pages
              <input value={pages} onChange={(e) => setPages(e.target.value)} placeholder="1,3-5" />
            </label>
          )}

          {operation === 'rotate' && (
            <label>
              Degrees
              <input value={degrees} onChange={(e) => setDegrees(e.target.value)} placeholder="90" />
            </label>
          )}

          {config.needsText && (
            <label>
              Watermark Text
              <input value={watermarkText} onChange={(e) => setWatermarkText(e.target.value)} placeholder="CONFIDENTIAL" />
            </label>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Run'}
          </button>
        </form>

        <div className="status-box">{status}</div>
      </div>
    </div>
  )
}

export default App
