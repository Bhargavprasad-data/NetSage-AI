import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Download, CheckCircle2, AlertCircle, File as FileIcon, X } from 'lucide-react';
import api from '../api';
import { fadeInUp } from '../transitions';

const fadeIn = fadeInUp;

const ImportExport: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExport = () => {
    window.open('http://localhost:8000/csv/export', '_blank');
  };

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setMessage('');
    try {
      const res = await api.post('/csv/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage(res.data.message);
      setMessageType('success');
      setFile(null);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Import failed. Please check your CSV format.');
      setMessageType('error');
    }
    setLoading(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.name.endsWith('.csv')) setFile(dropped);
  };

  const csvHeaders = [
    'hostname', 'device_type', 'issue_description', 'topology_note',
    'severity', 'expected_fault', 'osi_layer', 'concept_tag'
  ];

  return (
    <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1 } } }} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div className="page-header" variants={fadeIn}>
        <div>
          <h1 className="page-title">Import / Export</h1>
          <p className="page-subtitle">Bulk-load your troubleshooting dataset or export cases to CSV</p>
        </div>
      </motion.div>

      <div className="grid-2">
        {/* Export */}
        <motion.div className="card" variants={fadeIn}>
          <div className="section-header" style={{ marginBottom: '0.75rem' }}>
            <span className="section-title">Export Dataset</span>
            <Download size={16} color="var(--text-muted)" />
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1.5rem' }}>
            Export all current cases as a flat CSV file. Raw CLI <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.4rem', borderRadius: 5, fontSize: '0.8rem' }}>show_outputs</code> are excluded by design to keep the file manageable.
          </p>

          <div style={{ marginBottom: '1.5rem', background: 'rgba(0,0,0,0.25)', borderRadius: 10, padding: '0.875rem 1rem', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Exported Columns</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {csvHeaders.map(h => (
                <span key={h} style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem', background: 'rgba(88,101,242,0.1)', color: '#818cf8', borderRadius: 5, fontFamily: 'monospace' }}>
                  {h}
                </span>
              ))}
              <span style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem', background: 'rgba(100,116,139,0.1)', color: '#64748b', borderRadius: 5, fontFamily: 'monospace' }}>
                status
              </span>
            </div>
          </div>

          <motion.button
            className="btn btn-primary"
            onClick={handleExport}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Download size={16} /> Download CSV
          </motion.button>
        </motion.div>

        {/* Import */}
        <motion.div className="card" variants={fadeIn}>
          <div className="section-header" style={{ marginBottom: '0.75rem' }}>
            <span className="section-title">Import Dataset</span>
            <UploadCloud size={16} color="var(--text-muted)" />
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1.25rem' }}>
            Upload a CSV matching the schema above to bulk-create new cases. Existing cases will not be overwritten.
          </p>

          <form onSubmit={handleImport}>
            {/* Drop Zone */}
            <motion.div
              className="file-drop-zone"
              style={{ marginBottom: '1.25rem', borderColor: dragging ? 'var(--brand)' : file ? '#4ade80' : undefined, background: dragging ? 'rgba(88,101,242,0.06)' : file ? 'rgba(34,197,94,0.04)' : undefined }}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={e => setFile(e.target.files?.[0] || null)}
              />
              <AnimatePresence mode="wait">
                {file ? (
                  <motion.div key="file" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}>
                    <FileIcon size={32} color="#4ade80" style={{ margin: '0 auto 0.75rem' }} />
                    <div style={{ fontWeight: 600, color: '#4ade80', marginBottom: '0.25rem' }}>{file.name}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{(file.size / 1024).toFixed(1)} KB · Click to change</div>
                  </motion.div>
                ) : (
                  <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <UploadCloud size={32} color="var(--text-muted)" style={{ margin: '0 auto 0.75rem' }} />
                    <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                      {dragging ? 'Drop it here!' : 'Drag & drop or click to upload'}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>CSV files only</div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <motion.button
              type="submit"
              className="btn btn-primary"
              disabled={!file || loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {loading ? 'Importing…' : <><UploadCloud size={16} /> Upload & Import</>}
            </motion.button>
          </form>

          {/* Feedback */}
          <AnimatePresence>
            {message && (
              <motion.div
                className={`alert alert-${messageType}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                style={{ marginTop: '1rem', marginBottom: 0 }}
              >
                {messageType === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                <span>{message}</span>
                <motion.button style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }} onClick={() => setMessage('')} whileHover={{ scale: 1.1 }}>
                  <X size={14} />
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ImportExport;
