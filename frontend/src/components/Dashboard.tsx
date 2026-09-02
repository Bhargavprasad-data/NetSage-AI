import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import {
  FolderOpen, CheckCircle2, ShieldAlert, TrendingUp, Activity
} from 'lucide-react';
import api from '../api';
import { DashboardSkeleton } from './SkeletonLoaders';
import { fadeInUp, stagger } from '../transitions';

const COLORS = {
  OPEN: '#22d3ee',
  DIAGNOSED: '#fbbf24',
  REVIEWED: '#4ade80',
  RESOLVED: '#64748b',
  ACCEPTED: '#4ade80',
  EDITED: '#fbbf24',
  REJECTED: '#f87171',
};

const containerVariants = stagger;
const itemVariants = fadeInUp;

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'var(--tooltip-bg)',
        border: '1px solid var(--tooltip-border)',
        boxShadow: 'var(--card-shadow)',
        borderRadius: 10,
        padding: '0.6rem 1rem',
        fontSize: '0.8rem',
        color: 'var(--tooltip-text)',
        backdropFilter: 'blur(12px)',
      }}>
        <div style={{ fontWeight: 700, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>{payload[0].name}</div>
        <div style={{ color: payload[0].fill, fontWeight: 600 }}>{payload[0].value} cases</div>
      </div>
    );
  }
  return null;
};

const StatCard: React.FC<{
  label: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
  trend?: string;
  trendColor?: string;
}> = ({ label, value, icon, iconBg, trend, trendColor }) => (
  <motion.div className="stat-card" variants={itemVariants} whileHover={{ y: -3 }}>
    <div className="stat-card-icon" style={{ background: iconBg }}>{icon}</div>
    <div className="stat-value">{value}</div>
    <div className="stat-label">{label}</div>
    {trend && (
      <span className="stat-trend" style={{ color: trendColor, background: `${trendColor}18` }}>
        {trend}
      </span>
    )}
  </motion.div>
);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchStats = async () => {
    setError(false);
    try {
      const res = await api.get('/dashboard/stats');
      setStats(res.data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Poll every 30s to automatically refresh if backend comes back
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // Show shimmer indefinitely while loading or on error (retry in background)
  if (loading || error) {
    return <DashboardSkeleton />;
  }

  const statusData = Object.keys(stats.cases_by_status || {}).map(key => ({
    name: key,
    value: stats.cases_by_status[key],
    fill: COLORS[key as keyof typeof COLORS] || '#818cf8',
  }));

  const reviewData = Object.keys(stats.reviews || {}).map(key => ({
    name: key,
    value: stats.reviews[key],
    fill: COLORS[key as keyof typeof COLORS] || '#818cf8',
  }));

  const totalReviews = (stats.reviews?.ACCEPTED || 0) + (stats.reviews?.EDITED || 0) + (stats.reviews?.REJECTED || 0);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="dashboard-content"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div className="page-header" variants={itemVariants}>
          <div>
            <h1 className="page-title">Command Center</h1>
            <p className="page-subtitle">Real-time network intelligence & AI diagnostics overview</p>
          </div>
          <motion.div
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.5rem 1rem', borderRadius: 999,
              background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.25)',
              fontSize: '0.78rem', fontWeight: 600, color: '#4ade80'
            }}
            animate={{ opacity: [1, 0.6, 1] }}
            transition={{ duration: 2.5, repeat: Infinity }}
          >
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#4ade80' }} />
            Backend Live
          </motion.div>
        </motion.div>

        {/* Stat Cards */}
        <motion.div className="stats-grid" variants={itemVariants}>
          <StatCard
            label="Total Cases"
            value={stats.total_cases}
            icon={<FolderOpen size={22} color="#818cf8" strokeWidth={2} />}
            iconBg="rgba(88,101,242,0.15)"
            trend={`${stats.total_cases} total`}
            trendColor="#818cf8"
          />
          <StatCard
            label="AI Agreement Rate"
            value={`${(stats.agreement_percent || 0).toFixed(1)}%`}
            icon={<CheckCircle2 size={22} color="#4ade80" strokeWidth={2} />}
            iconBg="rgba(34,197,94,0.15)"
            trend="accepted / total"
            trendColor="#4ade80"
          />
          <StatCard
            label="Total Reviews"
            value={totalReviews}
            icon={<Activity size={22} color="#fbbf24" strokeWidth={2} />}
            iconBg="rgba(245,158,11,0.15)"
            trend={`${stats.reviews?.EDITED || 0} edited`}
            trendColor="#fbbf24"
          />
          <StatCard
            label="Rejections"
            value={stats.reviews?.REJECTED || 0}
            icon={<ShieldAlert size={22} color="#f87171" strokeWidth={2} />}
            iconBg="rgba(239,68,68,0.15)"
            trend="needs correction"
            trendColor="#f87171"
          />
        </motion.div>

        {/* Charts */}
        <motion.div className="charts-grid" variants={itemVariants}>
          {/* Cases by Status */}
          <div className="card">
            <div className="chart-card-title">Case Status Distribution</div>
            <div className="chart-card-sub">Breakdown of all case statuses</div>
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%" cy="50%"
                    innerRadius={68} outerRadius={105}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {statusData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    formatter={(val) => (
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{val}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <div className="empty-state-title">No data yet</div>
                <p className="empty-state-desc">Create and diagnose cases to see status breakdown.</p>
              </div>
            )}
          </div>

          {/* Review Decisions */}
          <div className="card">
            <div className="chart-card-title">AI-Human Agreement</div>
            <div className="chart-card-sub">Accepted / Edited / Rejected by reviewers</div>
            {reviewData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={reviewData} barSize={44}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: 'var(--text-muted)', fontSize: 11, fontWeight: 600 }}
                    axisLine={false} tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                    axisLine={false} tickLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--border-subtle)' }} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {reviewData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <div className="empty-state-title">No reviews yet</div>
                <p className="empty-state-desc">Submit human reviews to see agreement metrics.</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Agreement Metric Explainer */}
        <motion.div
          className="card"
          variants={itemVariants}
          style={{ borderColor: 'rgba(88,101,242,0.2)', background: 'rgba(88,101,242,0.04)' }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10, flexShrink: 0,
              background: 'rgba(88,101,242,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <TrendingUp size={20} color="#818cf8" />
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#818cf8', marginBottom: '0.25rem' }}>
                Agreement Metric Formula
              </div>
              <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.2rem 0.5rem', borderRadius: 5, color: '#4ade80', fontFamily: 'monospace' }}>
                  accepted / (accepted + edited + rejected)
                </code>
                <span style={{ marginLeft: '0.75rem' }}>
                  Edited cases do not count as AI-human agreement, even for minor corrections.
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Dashboard;
