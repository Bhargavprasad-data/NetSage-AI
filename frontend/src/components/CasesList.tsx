import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FolderOpen, ChevronRight, RefreshCw } from 'lucide-react';
import api from '../api';
import { TableSkeleton } from './SkeletonLoaders';
import { staggerFast, fadeInLeft } from '../transitions';

const containerVariants = staggerFast;
const rowVariants = fadeInLeft;

const CasesList: React.FC = () => {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchCases = async () => {
    setError(false);
    setLoading(true);
    try {
      const res = await api.get('/cases');
      setCases(res.data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
    const interval = setInterval(fetchCases, 30000);
    return () => clearInterval(interval);
  }, []);

  const severityColor: Record<string, string> = {
    HIGH: '#f87171', MEDIUM: '#fbbf24', LOW: '#4ade80', CRITICAL: '#c084fc'
  };

  return (
    <div>
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      >
        <div>
          <h1 className="page-title">Network Cases</h1>
          <p className="page-subtitle">All reported network issues and their diagnostic states</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <motion.button
            className="btn btn-ghost btn-sm"
            onClick={fetchCases}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
          >
            <RefreshCw size={15} /> Refresh
          </motion.button>
        </div>
      </motion.div>

      <AnimatePresence mode="wait">
        {(loading || error) ? (
          <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <TableSkeleton rows={6} cols={7} />
          </motion.div>
        ) : (
          <motion.div key="table" variants={containerVariants} initial="hidden" animate="visible">
            <div className="card table-container">
              <table>
                <thead>
                  <tr>
                    <th>Hostname</th>
                    <th>Device</th>
                    <th>Issue Description</th>
                    <th>Severity</th>
                    <th>OSI Layer</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {cases.map((c: any) => (
                      <motion.tr key={c.id} variants={rowVariants} layout>
                        <td>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>{c.hostname}</div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                            {new Date(c.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.825rem' }}>{c.device_type}</td>
                        <td>
                          <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {c.issue_description}
                          </div>
                        </td>
                        <td>
                          {c.severity ? (
                            <span className={`badge badge-${c.severity}`}>
                              <span className="badge-dot" style={{ background: severityColor[c.severity] || '#94a3b8' }} />
                              {c.severity}
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>—</span>
                          )}
                        </td>
                        <td style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                          {c.osi_layer || '—'}
                        </td>
                        <td>
                          <span className={`badge badge-${c.status}`}>
                            {c.status}
                          </span>
                        </td>
                        <td>
                          <Link to={`/cases/${c.id}`} style={{ textDecoration: 'none' }}>
                            <motion.button
                              className="btn btn-ghost btn-sm"
                              whileHover={{ scale: 1.04, x: 2 }}
                              whileTap={{ scale: 0.96 }}
                            >
                              View <ChevronRight size={14} />
                            </motion.button>
                          </Link>
                        </td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>

                  {cases.length === 0 && (
                    <tr>
                      <td colSpan={7}>
                        <div className="empty-state">
                          <FolderOpen size={48} className="empty-state-icon" />
                          <div className="empty-state-title">No cases found</div>
                          <p className="empty-state-desc">
                            Import a CSV dataset from the Import/Export page to load network troubleshooting cases.
                          </p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CasesList;
