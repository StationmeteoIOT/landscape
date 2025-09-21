import React from 'react';

export const metadata = {
  title: 'Station Météo',
  description: 'Dashboard météorologique avec interface inspirée de Death Stranding',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Roboto+Mono:wght@300;400;500;700&family=Montserrat:wght@300;400;500;700&family=Barlow+Condensed:wght@300;400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body style={{
        margin: 0,
        fontFamily: 'Rajdhani, system-ui, sans-serif',
        background: 'radial-gradient(1400px 700px at 85% -25%, rgba(0,145,255,0.10), transparent), linear-gradient(180deg, #0a0f14 0%, #080b10 100%)',
        color: '#e6edf3',
        minHeight: '100vh'
      }}>
        <style>{`
          *, *::before, *::after { box-sizing: border-box; }
          
          @font-face {
            font-family: 'DS-Digital';
            src: url('https://db.onlinewebfonts.com/t/8e22783d707ad140bffe18b2a3812529.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
          }
          
          body { 
            -webkit-font-smoothing: antialiased; 
            -moz-osx-font-smoothing: grayscale; 
            letter-spacing: 0.02em;
          }
          
          h1, h2, h3, h4, h5, h6 {
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            letter-spacing: 0.04em;
          }
          
          .ds-time {
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            letter-spacing: 0.06em;
          }
          
          .ds-mono {
            font-family: 'Share Tech Mono', 'Roboto Mono', monospace;
            letter-spacing: 0.03em;
          }
          
          .ds-title {
            font-family: 'Barlow Condensed', 'Rajdhani', sans-serif;
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }
          
          .card {
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            overflow: hidden;
            position: relative;
          }
          
          .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0,114,255,0.1), transparent);
            transition: left 0.7s ease;
            pointer-events: none;
          }
          
          .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 36px rgba(0,0,0,0.5), 0 0 5px rgba(0,114,255,0.3);
          }
          
          .card:hover::before {
            left: 100%;
          }
          
          a { 
            color: #7bd0ff; 
            text-decoration: none; 
            transition: all 0.2s ease;
            position: relative;
          }
          
          a.btn {
            display: inline-block;
            padding: 10px 24px;
            background: linear-gradient(90deg, rgba(0,145,255,0.2), rgba(0,114,255,0.2));
            border: 1px solid rgba(0,114,255,0.5);
            border-radius: 8px;
            color: #7bd0ff;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            overflow: hidden;
            position: relative;
          }
          
          a.btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0,114,255,0.2), transparent);
            transition: left 0.7s ease;
          }
          
          a.btn:hover {
            background: linear-gradient(90deg, rgba(0,145,255,0.3), rgba(0,114,255,0.3));
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
          }
          
          a.btn:hover::before {
            left: 100%;
          }
          
          a.btn:active {
            transform: translateY(1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          }
          
          nav a { 
            opacity: 0.9; 
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 14px;
            position: relative;
            overflow: hidden;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
          }
          
          nav a::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 2px;
            background: rgba(0,114,255,0.7);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            transform: translateX(-50%);
          }
          
          nav a:hover { 
            opacity: 1; 
            background: rgba(0,114,255,0.15);
          }
          
          nav a:hover::after {
            width: 70%;
          }
          
          nav a.active {
            background: rgba(0,114,255,0.15);
            font-weight: 600;
          }
          
          nav a.active::after {
            width: 70%;
            height: 2px;
            background: rgba(0,114,255,0.7);
          }
          
          /* Animations */
          @keyframes pulse { 
            0%,100%{ transform: scale(1); filter: drop-shadow(0 0 6px rgba(255,200,0,0.35)); } 
            50%{ transform: scale(1.05); filter: drop-shadow(0 0 16px rgba(255,200,0,0.5)); } 
          }
          
          @keyframes rain { 
            0%{ transform: translateY(0); opacity: 1; } 
            80%{ opacity: 1; } 
            100%{ transform: translateY(22px); opacity: 0; } 
          }
          
          @keyframes drift { 
            0% { transform: translate3d(0,0,0) scale(1); } 
            50% { transform: translate3d(10px, -10px, 0) scale(1.06); } 
            100% { transform: translate3d(0,0,0) scale(1); } 
          }
          
          @keyframes float { 
            0% { transform: translateY(0); } 
            50% { transform: translateY(-100vh); opacity: 0.8; } 
            50.1% { transform: translateY(100vh); opacity: 0; } 
            50.2% { opacity: 0.8; } 
            100% { transform: translateY(0); } 
          }
          
          @keyframes strand { 
            0% { transform: translateY(0) rotate(var(--rotation, 0deg)); opacity: 0; } 
            20% { opacity: 0.5; } 
            80% { opacity: 0.5; } 
            100% { transform: translateY(-50vh) rotate(var(--rotation, 0deg)); opacity: 0; } 
          }
          
          @keyframes glow { 
            0%, 100% { box-shadow: 0 0 15px rgba(0,114,255,0.1); } 
            50% { box-shadow: 0 0 25px rgba(0,114,255,0.2); } 
          }
          
          @keyframes blink { 
            0%, 100% { opacity: 0.4; } 
            50% { opacity: 1; } 
          }
          
          @keyframes scan-line {
            0% { 
              transform: translateY(-100%);
              opacity: 0.1;
            }
            50% { 
              opacity: 0.2; 
            }
            100% { 
              transform: translateY(100%);
              opacity: 0.1;
            }
          }
          
          /* Death Stranding inspired scroll bar */
          ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
          }
          
          ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.2);
            border-radius: 5px;
          }
          
          ::-webkit-scrollbar-thumb {
            background: rgba(0,114,255,0.3);
            border-radius: 5px;
            border: 2px solid rgba(0,0,0,0.2);
          }
          
          ::-webkit-scrollbar-thumb:hover {
            background: rgba(0,114,255,0.5);
          }
          
          /* Digital clock styling */
          .digital-clock {
            position: relative;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-shadow: 0 0 6px rgba(0,145,255,0.45);
            overflow: hidden;
          }
          
          .digital-clock::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, rgba(0,145,255,0.3) 50%, transparent 100%);
            opacity: 0.7;
            pointer-events: none;
          }
          
          .digital-clock::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(transparent 0%, rgba(0,10,20,0.05) 50%, transparent 100%);
            animation: scan-line 3s linear infinite;
            pointer-events: none;
          }
        `}</style>
        <header style={{ 
          maxWidth: 1200, 
          margin: '0 auto', 
          padding: '18px 20px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          borderBottom: '1px solid rgba(0,114,255,0.15)',
          backdropFilter: 'blur(10px)',
          position: 'sticky',
          top: 0,
          zIndex: 10,
          background: 'rgba(8,12,18,0.85)'
        }}>
          <div style={{ 
            fontWeight: 600, 
            letterSpacing: 0.8,
            fontSize: 20,
            background: 'linear-gradient(90deg, #7bd0ff, #0091ff)', 
            WebkitBackgroundClip: 'text', 
            color: 'transparent',
            textTransform: 'uppercase',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontFamily: "'Barlow Condensed', 'Rajdhani', sans-serif",
          }}>
            <span style={{ 
              display: 'inline-block', 
              width: '14px', 
              height: '14px', 
              borderRadius: '50%',
              background: 'rgba(0,114,255,0.3)',
              border: '2px solid rgba(0,114,255,0.5)',
              boxShadow: '0 0 10px rgba(0,114,255,0.2)',
              marginRight: '2px'
            }}></span>
            Station météo
            <span style={{ 
              position: 'absolute',
              bottom: '-8px',
              left: '0',
              width: '40%',
              height: '1px',
              background: 'linear-gradient(90deg, rgba(0,114,255,0.7), transparent)'
            }}></span>
          </div>
          <nav style={{ display: 'flex', gap: 12 }}>
            <a href="/" className={typeof window !== 'undefined' && window.location.pathname === '/' ? 'active' : ''}>
              Accueil
            </a>
            <a href="/data" className={typeof window !== 'undefined' && window.location.pathname === '/data' ? 'active' : ''}>
              Données
            </a>
          </nav>
        </header>
        {children}
        <footer style={{
          textAlign: 'center',
          padding: '24px 20px',
          marginTop: 40,
          opacity: 0.6,
          fontSize: 14,
          borderTop: '1px solid rgba(0,114,255,0.15)',
          letterSpacing: '0.05em',
          fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
          position: 'relative'
        }}>
          <div className="ds-mono" style={{ opacity: 0.8 }}>
            BRIDGES - Station météo | Projet N04 IOT
          </div>
          <div style={{ 
            position: 'absolute', 
            top: '-8px', 
            left: '50%', 
            transform: 'translateX(-50%)',
            width: '120px',
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(0,114,255,0.5), transparent)'
          }}></div>
        </footer>
      </body>
    </html>
  );
}
