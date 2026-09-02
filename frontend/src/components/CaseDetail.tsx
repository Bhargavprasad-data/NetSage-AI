import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, ChevronLeft, Terminal, Shield, CheckCircle2,
  Edit3, XCircle, AlertTriangle, Loader2
} from 'lucide-react';
import api from '../api';
import { Skeleton } from './SkeletonLoaders';
import { fadeInUp, stagger } from '../transitions';

const fadeIn = fadeInUp;
const staggerVariant = stagger;

const CaseDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<any>(null);
  const [diagnosisData, setDiagnosisData] = useState<any>(null);
  const [loadingCase, setLoadingCase] = useState(true);
  const [diagnosing, setDiagnosing] = useState(false);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState(false);

  const [reviewerName, setReviewerName] = useState('');
  const [decision, setDecision] = useState('ACCEPTED');
  const [feedback, setFeedback] = useState('');

  const fetchAll = async () => {
    try {
      const caseRes = await api.get(`/cases/${id}`);
      setCaseData(caseRes.data);
      if (caseRes.data.status !== 'OPEN') {
        try {
          const diagRes = await api.get(`/diagnoses/case/${id}`);
          setDiagnosisData(diagRes.data);
        } catch { }
      }
    } catch { } finally {
      setLoadingCase(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, [id]);

  const triggerDiagnosis = async () => {
    setDiagnosing(true);
    try {
      await api.post(`/diagnoses/case/${id}`);
      await fetchAll();
    } catch { }
    setDiagnosing(false);
  };

  const submitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingReview(true);
    try {
      await api.post('/reviews/', {
        diagnosis_id: diagnosisData.diagnosis.id,
        case_id: id,
        reviewer_name: reviewerName,
        decision,
        feedback
      });
      setReviewSuccess(true);
      await fetchAll();
    } catch { }
    setSubmittingReview(false);
  };

  if (loadingCase) {
    return (
      <div>
        <Skeleton style={{ height: 28, width: '30%', marginBottom: '2rem', borderRadius: 8 }} />
        <div className="grid-2">
          {[0, 1].map(i => (
            <div key={i} className="card">
              {[80, 60, 70, 50].map((w, j) => (
                <Skeleton key={j} style={{ height: 14, width: `${w}%`, marginBottom: '0.75rem', borderRadius: 6 }} />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="empty-state">
        <AlertTriangle size={48} className="empty-state-icon" />
        <div className="empty-state-title">Case not found</div>
      </div>
    );
  }

  const decisionConfig: Record<string, { color: string; icon: React.ReactNode }> = {
    ACCEPTED: { color: '#4ade80', icon: <CheckCircle2 size={14} /> },
    EDITED: { color: '#fbbf24', icon: <Edit3 size={14} /> },
    REJECTED: { color: '#f87171', icon: <XCircle size={14} /> },
  };

  return (
    <motion.div variants={staggerVariant} initial="hidden" animate="visible">
      {/* Back + Header */}
      <motion.div className="page-header" variants={fadeIn}>
        <div>
          <motion.button
            className="btn btn-ghost btn-sm"
            style={{ marginBottom: '0.75rem' }}
            onClick={() => navigate('/cases')}
            whileHover={{ x: -3 }}
          >
            <ChevronLeft size={16} /> Back to Cases
          </motion.button>
          <h1 className="page-title">{caseData.hostname}</h1>
          <p className="page-subtitle">{caseData.device_type} · {caseData.osi_layer || 'OSI Layer N/A'} · {caseData.concept_tag || 'No tag'}</p>
        </div>
        <span className={`badge badge-${caseData.status}`} style={{ fontSize: '0.875rem', padding: '0.4rem 1rem' }}>
          {caseData.status}
        </span>
      </motion.div>

      {/* Case Info + Diagnosis Side by Side */}
      <motion.div className="grid-2" variants={fadeIn} style={{ marginBottom: '1.5rem' }}>
        {/* Case Details */}
        <div className="card">
          <div className="section-header">
            <span className="section-title">Case Details</span>
            {caseData.severity && <span className={`badge badge-${caseData.severity}`}>{caseData.severity}</span>}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {[
              { label: 'Expected Fault', value: caseData.expected_fault },
              { label: 'Topology Note', value: caseData.topology_note },
            ].map(({ label, value }) => value && (
              <div key={label}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>{label}</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{value}</div>
              </div>
            ))}

            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>Issue Description</div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{caseData.issue_description}</div>
            </div>
          </div>

          {caseData.status === 'OPEN' && (
            <motion.button
              className="btn btn-primary"
              style={{ marginTop: '1.5rem', width: '100%', justifyContent: 'center' }}
              onClick={triggerDiagnosis}
              disabled={diagnosing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {diagnosing ? (
                <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}><Loader2 size={17} /></motion.div> Diagnosing…</>
              ) : (
                <><Brain size={17} /> Run AI Diagnosis</>
              )}
            </motion.button>
          )}
        </div>

        {/* AI Diagnosis Panel */}
        <AnimatePresence mode="wait">
          {diagnosisData ? (
            <motion.div
              key="diagnosis"
              className="card"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              style={{ border: '1px solid rgba(88,101,242,0.3)', background: 'rgba(88,101,242,0.04)' }}
            >
              <div className="section-header">
                <span className="section-title" style={{ color: '#818cf8' }}>
                  <Brain size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.375rem' }} />
                  AI Diagnosis
                </span>
                <span className={`badge badge-${diagnosisData.diagnosis.confidence}`}>
                  {diagnosisData.diagnosis.confidence} confidence
                </span>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.375rem' }}>Root Cause</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{diagnosisData.diagnosis.root_cause}</div>
              </div>

              {/* Evidence Verification */}
              {diagnosisData.verification_results && Object.keys(diagnosisData.verification_results).length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Evidence Verification</div>
                  <div className="evidence-list">
                    {Object.keys(diagnosisData.verification_results).map(key => {
                      const status = diagnosisData.verification_results[key];
                      const claim = diagnosisData.diagnosis.evidence?.[key];
                      return (
                        <motion.div
                          key={key}
                          className="evidence-item"
                          initial={{ opacity: 0, x: -8 }}
                          animate={{ opacity: 1, x: 0 }}
                        >
                          <span className={`badge badge-${status}`} style={{ flexShrink: 0 }}>{status}</span>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{claim || key}</span>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Next Commands */}
              {diagnosisData.diagnosis.next_commands?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                    <Terminal size={12} /> Next Commands
                  </div>
                  <div className="code-block">
                    {diagnosisData.diagnosis.next_commands.map((cmd: string) => (
                      <div key={cmd} className="code-block-line">
                        <span className="code-prompt">$</span>
                        <span>{cmd}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ) : caseData.status === 'OPEN' ? (
            <motion.div
              key="waiting"
              className="card"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
            >
              <div className="empty-state">
                <Brain size={48} className="empty-state-icon" />
                <div className="empty-state-title">No Diagnosis Yet</div>
                <p className="empty-state-desc">Click "Run AI Diagnosis" to trigger the rule engine and LLM pipeline.</p>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </motion.div>

      {/* Human Review Form */}
      <AnimatePresence>
        {caseData.status === 'DIAGNOSED' && diagnosisData && !reviewSuccess && (
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            style={{ border: '1px solid rgba(34,197,94,0.2)', background: 'rgba(34,197,94,0.02)' }}
          >
            <div className="section-header">
              <span className="section-title" style={{ color: '#4ade80' }}>
                <Shield size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.375rem' }} />
                Human-in-the-Loop Review
              </span>
            </div>

            <form onSubmit={submitReview}>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Reviewer Name</label>
                  <input
                    className="form-input"
                    required
                    value={reviewerName}
                    onChange={e => setReviewerName(e.target.value)}
                    placeholder="e.g. Dr. Sharma"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Decision</label>
                  <select className="form-select form-input" value={decision} onChange={e => setDecision(e.target.value)}>
                    <option value="ACCEPTED">✅ Accept — AI diagnosis is correct</option>
                    <option value="EDITED">✏️ Edit — Partially correct, corrected below</option>
                    <option value="REJECTED">❌ Reject — AI diagnosis is wrong</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  {decision === 'ACCEPTED' ? 'Additional Notes (Optional)' : 'Correction / Reason (Required for Edit/Reject)'}
                </label>
                <textarea
                  className="form-textarea form-input"
                  rows={3}
                  value={feedback}
                  onChange={e => setFeedback(e.target.value)}
                  placeholder={
                    decision === 'ACCEPTED'
                      ? 'Any observations…'
                      : 'Describe the correct root cause or why the AI was wrong…'
                  }
                  required={decision !== 'ACCEPTED'}
                />
              </div>

              {/* Decision badges preview */}
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
                {['ACCEPTED', 'EDITED', 'REJECTED'].map(d => (
                  <motion.span
                    key={d}
                    className={`badge badge-${d}`}
                    style={{ cursor: 'pointer', opacity: decision === d ? 1 : 0.35 }}
                    onClick={() => setDecision(d)}
                    whileHover={{ scale: 1.06 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {decisionConfig[d].icon} {d}
                  </motion.span>
                ))}
              </div>

              <motion.button
                type="submit"
                className="btn btn-primary"
                disabled={submittingReview}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {submittingReview ? (
                  <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}><Loader2 size={16} /></motion.div> Submitting…</>
                ) : (
                  <><Shield size={16} /> Submit Review</>
                )}
              </motion.button>
            </form>
          </motion.div>
        )}

        {(caseData.status === 'REVIEWED' || reviewSuccess) && (
          <motion.div
            className="alert alert-success"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <CheckCircle2 size={18} />
            <div>
              <strong>Review Submitted</strong>
              <div style={{ fontSize: '0.825rem', marginTop: '0.25rem', opacity: 0.8 }}>
                This case has been reviewed. A Responsible AI log has been automatically created if the diagnosis was edited or rejected.
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default CaseDetail;
