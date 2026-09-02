import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', style }) => (
  <div className={`skeleton ${className}`} style={style} />
);

export const StatCardSkeleton: React.FC = () => (
  <div className="stat-card">
    <Skeleton style={{ width: 44, height: 44, borderRadius: 12, marginBottom: '1.25rem' }} />
    <Skeleton style={{ height: 40, width: '60%', marginBottom: '0.5rem', borderRadius: 8 }} />
    <Skeleton style={{ height: 12, width: '40%', borderRadius: 6 }} />
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="card" style={{ padding: '1.5rem' }}>
    <Skeleton style={{ height: 14, width: '35%', marginBottom: '0.5rem', borderRadius: 6 }} />
    <Skeleton style={{ height: 11, width: '50%', marginBottom: '1.5rem', borderRadius: 5 }} />
    <Skeleton style={{ height: 260, borderRadius: 12 }} />
  </div>
);

export const TableRowSkeleton: React.FC<{ cols?: number }> = ({ cols = 7 }) => (
  <tr>
    {Array.from({ length: cols }).map((_, i) => (
      <td key={i} style={{ padding: '1rem 1.25rem' }}>
        <Skeleton style={{ height: 14, width: i === 2 ? '80%' : '60%', borderRadius: 6 }} />
      </td>
    ))}
  </tr>
);

export const DashboardSkeleton: React.FC = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <div style={{ marginBottom: '2rem' }}>
      <Skeleton style={{ height: 28, width: '220px', borderRadius: 8, marginBottom: '0.5rem' }} />
      <Skeleton style={{ height: 14, width: '300px', borderRadius: 6 }} />
    </div>
    <div className="stats-grid">
      {[...Array(4)].map((_, i) => <StatCardSkeleton key={i} />)}
    </div>
    <div className="charts-grid">
      <ChartSkeleton />
      <ChartSkeleton />
    </div>
  </motion.div>
);

export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({ rows = 6, cols = 7 }) => (
  <div className="card table-container">
    <table>
      <thead>
        <tr>
          {Array.from({ length: cols }).map((_, i) => (
            <th key={i}>
              <Skeleton style={{ height: 10, width: 70, borderRadius: 5 }} />
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: rows }).map((_, i) => (
          <TableRowSkeleton key={i} cols={cols} />
        ))}
      </tbody>
    </table>
  </div>
);
