import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedLogoProps {
  expanded?: boolean;
  size?: number;
}

export const AnimatedLogo: React.FC<AnimatedLogoProps> = ({ expanded = true, size = 38 }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
      {/* Dynamic Animated Logo Emblem */}
      <div
        style={{
          position: 'relative',
          width: size,
          height: size,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Ambient Glow Aura */}
        <motion.div
          style={{
            position: 'absolute',
            inset: -4,
            borderRadius: '12px',
            background: 'radial-gradient(circle, rgba(88, 101, 242, 0.45) 0%, rgba(139, 92, 246, 0.2) 60%, transparent 100%)',
            filter: 'blur(8px)',
            zIndex: 0,
          }}
          animate={{
            scale: [1, 1.25, 1],
            opacity: [0.6, 0.9, 0.6],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* Outer Orbiting Ring 1 */}
        <motion.div
          style={{
            position: 'absolute',
            inset: -2,
            borderRadius: '12px',
            border: '1.5px dashed rgba(129, 140, 248, 0.5)',
            zIndex: 1,
            pointerEvents: 'none',
          }}
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Ping / Radar Wave Pulse */}
        <motion.div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '10px',
            border: '2px solid rgba(34, 211, 238, 0.8)',
            zIndex: 1,
            pointerEvents: 'none',
          }}
          animate={{
            scale: [1, 1.45, 1.6],
            opacity: [0.8, 0.3, 0],
          }}
          transition={{
            duration: 2.2,
            repeat: Infinity,
            ease: 'easeOut',
          }}
        />

        {/* Main Logo Cube / Shield Body */}
        <motion.div
          style={{
            position: 'relative',
            width: size,
            height: size,
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2,
            boxShadow: '0 4px 16px rgba(79, 70, 229, 0.4), inset 0 1px 1px rgba(255,255,255,0.3)',
            overflow: 'hidden',
          }}
          animate={{
            y: [-1.5, 1.5, -1.5],
          }}
          transition={{
            duration: 3.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          whileHover={{ scale: 1.1, rotate: 6 }}
        >
          {/* Moving Light Glare / Sheen effect */}
          <motion.div
            style={{
              position: 'absolute',
              top: '-50%',
              left: '-50%',
              width: '200%',
              height: '200%',
              background: 'linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.4) 50%, transparent 60%)',
              pointerEvents: 'none',
            }}
            animate={{
              x: ['-100%', '100%'],
              y: ['-100%', '100%'],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              repeatDelay: 1.5,
              ease: 'easeInOut',
            }}
          />

          {/* Animated SVG Network Nodes inside */}
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style={{ position: 'relative', zIndex: 3 }}>
            {/* Connection Lines with Moving Dash Array */}
            <motion.path
              d="M12 4L4 18H20L12 4Z"
              stroke="#ffffff"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0.8, strokeDashoffset: 0 }}
              animate={{
                strokeDashoffset: [0, -24],
                strokeOpacity: [0.7, 1, 0.7],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: 'linear',
              }}
              strokeDasharray="4 2"
            />
            
            {/* Cross Lines */}
            <motion.path
              d="M12 4V18 M4 18L16 11 M20 18L8 11"
              stroke="rgba(255,255,255,0.5)"
              strokeWidth="1.2"
              strokeLinecap="round"
            />

            {/* Top Node */}
            <motion.circle
              cx="12"
              cy="4"
              r="2.5"
              fill="#22d3ee"
              stroke="#ffffff"
              strokeWidth="1"
              animate={{
                scale: [1, 1.3, 1],
                fill: ['#22d3ee', '#38bdf8', '#22d3ee'],
              }}
              transition={{
                duration: 1.8,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />

            {/* Left Node */}
            <motion.circle
              cx="4"
              cy="18"
              r="2.5"
              fill="#a855f7"
              stroke="#ffffff"
              strokeWidth="1"
              animate={{
                scale: [1.2, 1, 1.2],
                fill: ['#a855f7', '#c084fc', '#a855f7'],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 0.3,
              }}
            />

            {/* Right Node */}
            <motion.circle
              cx="20"
              cy="18"
              r="2.5"
              fill="#38bdf8"
              stroke="#ffffff"
              strokeWidth="1"
              animate={{
                scale: [1, 1.35, 1],
                fill: ['#38bdf8', '#4ade80', '#38bdf8'],
              }}
              transition={{
                duration: 2.2,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 0.6,
              }}
            />

            {/* Center Core Node */}
            <motion.circle
              cx="12"
              cy="13"
              r="2"
              fill="#ffffff"
              animate={{
                scale: [0.8, 1.4, 0.8],
                opacity: [0.7, 1, 0.7],
              }}
              transition={{
                duration: 1.4,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </svg>
        </motion.div>
      </div>

      {/* Brand Text with Shimmering Gradient */}
      <motion.div
        className="sidebar-logo-text"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: expanded ? 1 : 0, x: expanded ? 0 : -10 }}
        transition={{ duration: 0.2, delay: expanded ? 0.08 : 0 }}
        style={{ pointerEvents: 'none', display: 'flex', flexDirection: 'column' }}
      >
        <motion.span
          className="sidebar-logo-title"
          style={{
            background: 'linear-gradient(90deg, #ffffff 0%, #818cf8 35%, #22d3ee 70%, #ffffff 100%)',
            backgroundSize: '200% auto',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            display: 'inline-block',
            fontWeight: 800,
            fontSize: '1.05rem',
            letterSpacing: '-0.02em',
          }}
          animate={{
            backgroundPosition: ['0% center', '200% center'],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          NetSage AI
        </motion.span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <motion.div
            style={{
              width: 5,
              height: 5,
              borderRadius: '50%',
              background: '#22c55e',
            }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <span className="sidebar-logo-sub" style={{ fontSize: '0.65rem', letterSpacing: '0.08em', color: '#94a3b8' }}>
            Autonomous NetOps
          </span>
        </div>
      </motion.div>
    </div>
  );
};
