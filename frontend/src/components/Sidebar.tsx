import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderOpen,
  UploadCloud,
  ShieldCheck,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../ThemeContext';

import { AnimatedLogo } from './AnimatedLogo';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, description: 'Overview & metrics' },
  { path: '/cases', label: 'Cases', icon: FolderOpen, description: 'Network issues' },
  { path: '/import-export', label: 'Import / Export', icon: UploadCloud, description: 'CSV data tools' },
];

const Sidebar: React.FC = () => {
  const [expanded, setExpanded] = React.useState(false);
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="sidebar-rail">
      <motion.div
        className="sidebar-panel"
        initial={false}
        animate={{ width: expanded ? 260 : 72 }}
        transition={{ type: 'spring', stiffness: 340, damping: 36, mass: 0.8 }}
        onHoverStart={() => setExpanded(true)}
        onHoverEnd={() => setExpanded(false)}
      >
        {/* Logo with Dynamic Animations */}
        <div className="sidebar-logo">
          <AnimatedLogo expanded={expanded} size={38} />
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navItems.map((item, index) => {
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className="nav-item"
                style={{ textDecoration: 'none' }}
              >
                {() => (
                  <>
                    {/* Active background pill */}
                    <AnimatePresence>
                      {isActive && (
                        <motion.div
                          layoutId="active-pill"
                          style={{
                            position: 'absolute',
                            inset: 0,
                            background: 'linear-gradient(135deg, rgba(88,101,242,0.2), rgba(139,92,246,0.15))',
                            borderRadius: 10,
                            border: '1px solid rgba(88,101,242,0.3)',
                          }}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 0.25 }}
                        />
                      )}
                    </AnimatePresence>

                    {/* Hover background */}
                    {!isActive && (
                      <motion.div
                        className="nav-hover-bg"
                        style={{
                          position: 'absolute',
                          inset: 0,
                          borderRadius: 10,
                          background: 'rgba(255,255,255,0.04)',
                          opacity: 0,
                        }}
                        whileHover={{ opacity: 1 }}
                        transition={{ duration: 0.15 }}
                      />
                    )}

                    {/* Icon */}
                    <motion.div
                      className="nav-item-icon"
                      style={{ position: 'relative', zIndex: 1 }}
                      whileHover={{ scale: 1.15 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                    >
                      <Icon
                        size={20}
                        strokeWidth={isActive ? 2.5 : 1.75}
                        color={isActive ? '#818cf8' : '#64748b'}
                      />
                    </motion.div>

                    {/* Label */}
                    <motion.span
                      className="nav-item-label"
                      style={{ position: 'relative', zIndex: 1, color: isActive ? '#818cf8' : '#94a3b8' }}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: expanded ? 1 : 0, x: expanded ? 0 : -8 }}
                      transition={{ duration: 0.18, delay: expanded ? 0.05 + index * 0.04 : 0 }}
                    >
                      {item.label}
                    </motion.span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <motion.div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.875rem',
              padding: '0.6rem 0.625rem',
              borderRadius: 10,
              cursor: 'pointer',
              overflow: 'hidden',
            }}
            whileHover={{ background: 'rgba(255,255,255,0.04)' }}
          >
            <motion.div
              style={{
                width: 36,
                height: 36,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #22c55e, #06b6d4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
              whileHover={{ scale: 1.05 }}
            >
              <ShieldCheck size={18} color="#fff" strokeWidth={2} />
            </motion.div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: expanded ? 1 : 0 }}
              transition={{ duration: 0.18, delay: expanded ? 0.12 : 0 }}
              style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>Human-in-Loop</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Responsible AI</div>
            </motion.div>
          </motion.div>

          {/* Theme Toggle Button */}
          <motion.button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          >
            <motion.div
              className="theme-toggle-icon"
              animate={{ rotate: theme === 'dark' ? 0 : 180 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              {theme === 'dark' ? (
                <Moon size={16} color="#818cf8" strokeWidth={2.2} />
              ) : (
                <Sun size={16} color="#f59e0b" strokeWidth={2.2} />
              )}
            </motion.div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: expanded ? 1 : 0 }}
              transition={{ duration: 0.18 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}
            >
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                Click to switch
              </span>
            </motion.div>
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

export default Sidebar;
