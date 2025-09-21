"use client";

import { useEffect, useMemo, useState } from 'react';
import { formatDateFR } from '../lib/date';

type Measure = {
  id: number;
  created_at: string;
  temperature?: number;
  humidite?: number;
  pression?: number;
  co2?: number;
  humidite_surface?: number;
  pluie_detectee?: 0 | 1 | boolean;
  indice_uv?: number;
};

function Card({ title, value, subtitle }:{ title:string; value:string; subtitle?:string }){
  return (
    <div className="card" style={{
      background: 'linear-gradient(180deg, rgba(10,14,20,0.95), rgba(6,10,16,0.95))',
      border: '1px solid rgba(0,114,255,0.25)',
      borderRadius: 16,
      padding: 16,
      boxShadow: '0 12px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04)',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      transition: 'transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
    }}>
      <div style={{ 
        opacity: 0.7, 
        fontSize: 12, 
        letterSpacing: 1, 
        textTransform: 'uppercase', 
        fontFamily: "'Barlow Condensed', 'Rajdhani', sans-serif",
        marginBottom: 4,
        fontWeight: 500
      }}>{title}</div>
      <div style={{ 
        fontSize: 28, 
        marginTop: 6,
        fontFamily: "'Rajdhani', sans-serif",
        letterSpacing: '0.05em',
        fontWeight: 300
      }}>{value}</div>
      {subtitle && (
        <div style={{ 
          opacity: 0.5, 
          fontSize: 12, 
          marginTop: 4,
          fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
          letterSpacing: '0.03em'
        }}>{subtitle}</div>
      )}
    </div>
  );
}

function SunIcon() {
  return (
    <div style={{ position: 'relative', width: 120, height: 120 }}>
      <div style={{
        position: 'absolute', inset: 0,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255,215,0,0.9) 0%, rgba(255,170,0,0.85) 60%, rgba(0,0,0,0) 62%)',
        animation: 'pulse 3s ease-in-out infinite'
      }}/>
      <div style={{
        position: 'absolute', inset: -10,
        borderRadius: '50%',
        border: '2px solid rgba(0,114,255,0.35)',
        boxShadow: '0 0 40px rgba(0,114,255,0.35) inset',
        filter: 'blur(0.3px)'
      }}/>
    </div>
  );
}

function RainIcon() {
  return (
    <div style={{ position: 'relative', width: 140, height: 120 }}>
      {/* Cloud */}
      <div style={{
        position: 'absolute', top: 25, left: 20, right: 20, height: 60,
        background: 'linear-gradient(180deg, #202a36, #161d26)',
        borderRadius: 30,
        boxShadow: '0 10px 25px rgba(0,0,0,0.4)'
      }}/>
      {/* Raindrops */}
      {[...Array(8)].map((_, i) => (
        <div key={i} style={{
          position: 'absolute', top: 70, left: 20 + i*12,
          width: 3, height: 16,
          background: 'linear-gradient(180deg, rgba(0,160,255,0.9), rgba(0,114,255,0.6))',
          borderRadius: 2,
          animation: `rain 1.2s ${i*0.12}s linear infinite`
        }}/>
      ))}
    </div>
  );
}

function CloudIcon() {
  return (
    <div style={{ position: 'relative', width: 140, height: 120 }}>
      {/* Clouds */}
      <div style={{
        position: 'absolute', top: 35, left: 30, width: 80, height: 50,
        background: 'linear-gradient(180deg, #202a36, #161d26)',
        borderRadius: 25,
        boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
        animation: 'drift 10s ease-in-out infinite'
      }}/>
      <div style={{
        position: 'absolute', top: 25, left: 20, width: 50, height: 40,
        background: 'linear-gradient(180deg, #232d39, #181e29)',
        borderRadius: 20,
        boxShadow: '0 8px 20px rgba(0,0,0,0.3)',
        animation: 'drift 14s ease-in-out infinite reverse'
      }}/>
      <div style={{
        position: 'absolute', top: 45, right: 20, width: 40, height: 30,
        background: 'linear-gradient(180deg, #1d2530, #141a23)',
        borderRadius: 15,
        boxShadow: '0 6px 15px rgba(0,0,0,0.25)',
        animation: 'drift 12s ease-in-out infinite'
      }}/>
    </div>
  );
}

export default function Page() {
  const [data, setData] = useState<Measure[]>([]);
  const [loading, setLoading] = useState(true);
  const [now, setNow] = useState<Date>(new Date());

  async function load() {
    try {
      const res = await fetch('/api/measures', { cache: 'no-store' });
      const json = await res.json();
      setData(Array.isArray(json) ? json : []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const last = data?.[0];
  const avg = useMemo(()=> (key:string) => {
    if (!data?.length) return '-';
    const v = data.map((r:any)=> r[key]).filter((x:number)=> typeof x === 'number');
    if (!v.length) return '-';
    const m = v.reduce((a:number,b:number)=>a+b,0)/v.length;
    return m.toFixed(1);
  }, [data]);

  const isRain = Boolean(last?.pluie_detectee);
  const isSunny = !isRain && (typeof last?.indice_uv === 'number' ? last!.indice_uv! >= 2.5 : false) && (typeof last?.humidite === 'number' ? last!.humidite! <= 70 : true);

  // Format time with hours, minutes, seconds
  const timeString = now.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
  
  // Format date separately
  const dateString = now.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return (
    <main style={{ maxWidth: 1200, margin: '20px auto 40px', padding: '0 20px', position: 'relative' }}>
      {/* Animated background blobs */}
      <div aria-hidden style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, overflow: 'hidden' }}>
        {/* Primary animated blobs */}
        <div style={{ position: 'absolute', width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,145,255,0.18), rgba(0,0,0,0))', top: '5%', left: '10%', filter: 'blur(40px)', animation: 'drift 20s ease-in-out infinite' }}/>
        <div style={{ position: 'absolute', width: 360, height: 360, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,120,255,0.15), rgba(0,0,0,0))', bottom: '15%', right: '5%', filter: 'blur(50px)', animation: 'drift 26s ease-in-out infinite reverse' }}/>
        <div style={{ position: 'absolute', width: 220, height: 220, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,200,255,0.12), rgba(0,0,0,0))', top: '30%', right: '25%', filter: 'blur(30px)', animation: 'drift 24s ease-in-out infinite' }}/>
        
        {/* Secondary particles */}
        {[...Array(15)].map((_, i) => (
          <div key={i} style={{
            position: 'absolute',
            width: 2 + Math.random() * 4,
            height: 2 + Math.random() * 4,
            borderRadius: '50%',
            background: 'rgba(0,145,255,0.4)',
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            filter: 'blur(1px)',
            animation: `float ${10 + Math.random() * 20}s linear infinite`
          }}/>
        ))}
        
        {/* Strand effects (Death Stranding inspired) */}
        {[...Array(5)].map((_, i) => (
          <div key={`strand-${i}`} style={{
            position: 'absolute',
            width: 1,
            height: 80 + Math.random() * 120,
            background: 'linear-gradient(to bottom, rgba(0,145,255,0), rgba(0,145,255,0.1), rgba(0,145,255,0))',
            top: `${Math.random() * 80}%`,
            left: `${Math.random() * 100}%`,
            transform: `rotate(${Math.random() * 20 - 10}deg)`,
            animation: `strand ${15 + Math.random() * 25}s ease-in-out infinite`
          }}/>
        ))}
      </div>
      
      <section style={{
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        background: 'linear-gradient(180deg, rgba(8,12,18,0.85), rgba(5,9,14,0.85))',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(0,114,255,0.25)',
        borderRadius: 16, 
        padding: '24px 30px', 
        marginBottom: 24,
        boxShadow: '0 18px 40px rgba(0,0,0,0.5)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 style={{ 
            margin: 0, 
            fontSize: 32, 
            background: 'linear-gradient(90deg, #7bd0ff, #0091ff)', 
            WebkitBackgroundClip: 'text', 
            color: 'transparent',
            fontWeight: 600,
            letterSpacing: '0.03em',
            marginBottom: 10,
            fontFamily: "'Rajdhani', sans-serif"
          }}>Conditions actuelles</h1>
          <div className="digital-clock ds-time" style={{ 
            fontSize: 18, 
            marginTop: 8,
            position: 'relative',
            padding: '8px 0'
          }}>
            <span style={{ 
              fontSize: 36, 
              fontWeight: 700, 
              letterSpacing: '0.06em',
              color: '#7bd0ff'
            }}>{timeString}</span>
          </div>
          <div style={{ 
            opacity: 0.75, 
            marginTop: 8, 
            fontSize: 15,
            fontFamily: "'Rajdhani', sans-serif",
            letterSpacing: '0.03em',
            fontWeight: 300
          }}>{dateString}</div>
        </div>
        
        <div className="weather-icon-container" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 140,
          height: 140,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(8,16,30,0.6) 0%, rgba(5,10,20,0.4) 70%)',
          boxShadow: 'inset 0 0 20px rgba(0,0,0,0.3)',
          animation: 'glow 4s ease-in-out infinite',
          border: '1px solid rgba(0,114,255,0.2)',
          position: 'relative',
          zIndex: 1
        }}>
          {isRain ? <RainIcon/> : (isSunny ? <SunIcon/> : <CloudIcon/>)}
        </div>
        
        {/* Scanline effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(transparent 0%, rgba(0,10,20,0.03) 50%, transparent 100%)',
          animation: 'scan-line 8s linear infinite',
          pointerEvents: 'none',
          zIndex: 0
        }}></div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 320px) 1fr', gap: 24, alignItems: 'start', position: 'relative', zIndex: 1 }}>
        {/* Weather side panel */}
        <aside style={{
          position: 'sticky', top: 20,
          background: 'linear-gradient(180deg, rgba(8,12,18,0.85), rgba(5,9,14,0.85))',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(0,114,255,0.25)',
          borderRadius: 16,
          padding: 20,
          boxShadow: '0 18px 40px rgba(0,0,0,0.5)',
          overflow: 'hidden'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, position: 'relative', zIndex: 1 }}>
            <div>
              <div style={{ 
                opacity: 0.7, 
                fontSize: 14, 
                letterSpacing: 1, 
                textTransform: 'uppercase',
                fontFamily: "'Barlow Condensed', 'Rajdhani', sans-serif",
                fontWeight: 600
              }}>Météo</div>
              <div style={{ 
                fontSize: 22, 
                marginTop: 6, 
                fontWeight: 500,
                color: isRain ? '#7bd0ff' : (isSunny ? '#ffd36e' : '#b6a0ff'),
                fontFamily: "'Rajdhani', sans-serif"
              }}>
                {isRain ? 'Pluie détectée' : (isSunny ? 'Beau temps probable' : 'Ciel variable')}
              </div>
              <div style={{ 
                opacity: 0.6, 
                fontSize: 12, 
                marginTop: 6,
                fontFamily: "'Rajdhani', sans-serif",
                letterSpacing: '0.03em',
                fontWeight: 300
              }}>
                Dernière mesure: {formatDateFR(last?.created_at)}
              </div>
            </div>
          </div>
          
          <div style={{ 
            position: 'relative', 
            marginTop: 16, 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, minmax(0,1fr))', 
            gap: 12,
            zIndex: 1
          }}>
            <Card title="Temp (°C)" value={last? `${last.temperature?.toFixed?.(1) ?? '-'}` : '-'} subtitle={`moy: ${avg('temperature')}`}/>
            <Card title="Hum (%)" value={last? `${last.humidite?.toFixed?.(1) ?? '-'}` : '-'} subtitle={`moy: ${avg('humidite')}`}/>
            <Card title="Press (hPa)" value={last? `${last.pression?.toFixed?.(1) ?? '-'}` : '-'} subtitle={`moy: ${avg('pression')}`}/>
            <Card title="UV" value={last? `${last.indice_uv?.toFixed?.(1) ?? '-'}` : '-'} subtitle={`moy: ${avg('indice_uv')}`}/>
          </div>
          
          <div style={{ 
            marginTop: 16, 
            padding: '12px 16px', 
            background: 'rgba(0,114,255,0.1)', 
            borderRadius: 8, 
            fontSize: 14,
            position: 'relative',
            fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
            letterSpacing: '0.03em',
            border: '1px solid rgba(0,114,255,0.2)',
            boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.2)',
            transition: 'all 0.3s ease',
            zIndex: 1
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span>CO2:</span>
              <span className="ds-mono" style={{ color: '#74e0c9', fontFamily: "'Rajdhani', sans-serif", fontWeight: 300 }}>{last? `${last.co2?.toFixed?.(0) ?? '-'} ppm` : '-'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Humidité surface:</span>
              <span className="ds-mono" style={{ color: '#74e0c9', fontFamily: "'Rajdhani', sans-serif", fontWeight: 300 }}>{last? `${last.humidite_surface?.toFixed?.(1) ?? '-'}%` : '-'}</span>
            </div>
          </div>
          
          {/* Scanline effect */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'linear-gradient(transparent 0%, rgba(0,10,20,0.03) 50%, transparent 100%)',
            animation: 'scan-line 10s linear infinite',
            pointerEvents: 'none',
            zIndex: 0
          }}></div>
        </aside>

        {/* Main content (simplified) */}
        <section>
          <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ 
              color: '#7bd0ff', 
              display: 'flex', 
              alignItems: 'center', 
              gap: 8,
              fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
              fontSize: 14,
              letterSpacing: '0.05em'
            }}>
              <span style={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                background: '#7bd0ff', 
                animation: 'blink 2s ease-in-out infinite',
                boxShadow: '0 0 8px rgba(123, 208, 255, 0.5)'
              }}></span>
              Mise à jour auto (15s)
            </span>
            {loading && (
              <span style={{ 
                opacity: 0.6, 
                fontSize: 12,
                fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace"
              }}>(chargement…)</span>
            )}
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, minmax(0,1fr))', 
            gap: 16,
            height: 140  // Fixed height for consistent cards
          }}>
            <Card 
              title="Température actuelle" 
              value={last? `${last.temperature?.toFixed?.(1) ?? '-' } °C` : '-'} 
              subtitle={`maj: ${formatDateFR(last?.created_at)}`}
            />
            <Card 
              title="Humidité actuelle" 
              value={last? `${last.humidite?.toFixed?.(1) ?? '-' } %` : '-'} 
              subtitle={`UV: ${last?.indice_uv?.toFixed?.(1) ?? '-'}`}
            />
            <Card 
              title="Pression actuelle" 
              value={last? `${last.pression?.toFixed?.(1) ?? '-' } hPa` : '-'} 
              subtitle={isRain ? 'Pluie détectée' : (isSunny ? 'Beau temps probable' : 'Ciel variable')}
            />
          </div>

          <div className="card" style={{ 
            marginTop: 24,
            background: 'linear-gradient(180deg, rgba(8,12,18,0.85), rgba(5,9,14,0.85))',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(0,114,255,0.25)',
            borderRadius: 16,
            padding: '24px 20px',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{ 
              fontSize: 18, 
              marginBottom: 16,
              fontFamily: "'Rajdhani', sans-serif",
              letterSpacing: '0.04em',
              position: 'relative',
              zIndex: 1,
              fontWeight: 500
            }}>Besoin de détails et d'historique ?</div>
            
            <a 
              href="/data" 
              className="btn"
              style={{
                position: 'relative',
                zIndex: 1,
                fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
                letterSpacing: '0.05em'
              }}
            >
              Voir toutes les données →
            </a>
            
            {/* Scanline effect */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              background: 'linear-gradient(transparent 0%, rgba(0,10,20,0.03) 50%, transparent 100%)',
              animation: 'scan-line 8s linear infinite',
              pointerEvents: 'none',
              zIndex: 0
            }}></div>
          </div>
        </section>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{ transform: scale(1); filter: drop-shadow(0 0 6px rgba(255,200,0,0.35)); } 50%{ transform: scale(1.05); filter: drop-shadow(0 0 16px rgba(255,200,0,0.5)); } }
        @keyframes rain { 0%{ transform: translateY(0); opacity: 1; } 80%{ opacity: 1; } 100%{ transform: translateY(22px); opacity: 0; } }
        @keyframes drift { 0% { transform: translate3d(0,0,0) scale(1); } 50% { transform: translate3d(10px, -10px, 0) scale(1.06); } 100% { transform: translate3d(0,0,0) scale(1); } }
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
      `}</style>
    </main>
  );
}
