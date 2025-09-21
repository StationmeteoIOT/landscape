"use client";

import { useEffect, useMemo, useState } from 'react';
import { formatDateFR, parseCreatedAt } from '../../lib/date';

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

export default function DataPage() {
  const [data, setData] = useState<Measure[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setLoading(true);
      const res = await fetch('/api/measures', { cache: 'no-store' });
      const json = await res.json();
      setData(Array.isArray(json) ? json : []);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { 
    load(); 
    const intervalId = setInterval(load, 60000); // Refresh every minute
    return () => clearInterval(intervalId);
  }, []);

  const series = useMemo(() => {
    // Filtrer les données pour n'avoir qu'une mesure toutes les 10 minutes
    // Cela rendra les graphiques plus propres et plus lisibles
    const filterByTimeInterval = (data: Measure[]) => {
      if (!data.length) return [];
      
      const filteredData = [data[0]]; // Garder toujours la mesure la plus récente
      let lastTimestamp = parseCreatedAt(data[0].created_at)?.getTime() || 0;
      
      // Parcourir le reste des données et ne garder que celles espacées d'au moins 10 minutes
      for (let i = 1; i < data.length; i++) {
        const currentTimestamp = parseCreatedAt(data[i].created_at)?.getTime() || 0;
        // 600000 ms = 10 minutes
        if (Math.abs(currentTimestamp - lastTimestamp) >= 600000) {
          filteredData.push(data[i]);
          lastTimestamp = currentTimestamp;
        }
      }
      
      return filteredData;
    };
    
    const filteredData = filterByTimeInterval(data);
    console.log(`Données filtrées: ${filteredData.length} sur ${data.length} mesures (1 point toutes les 10 min)`);
    
    const toPairs = (key: keyof Measure) => {
      const pairs = filteredData
        .filter(m => typeof m[key] === 'number' && m[key] !== null)
        .map(m => {
          // Use our enhanced date parser
          const parsedDate = parseCreatedAt(m.created_at);
          
          // Ensure we have a valid date (fallback to entry index if date is invalid)
          const time = parsedDate && !isNaN(parsedDate.getTime()) 
            ? parsedDate.getTime() 
            : Date.now() - (filteredData.indexOf(m) * 600000); // Fallback: now - index*10min
          
          return { 
            t: time, 
            v: (m[key] as number),
            label: formatDateFR(m.created_at) // Format date for display
          };
        });
      
      // Sort by time to ensure line drawing works correctly
      return pairs.sort((a, b) => a.t - b.t);
    };
    
    return {
      temperature: toPairs('temperature'),
      humidite: toPairs('humidite'),
      pression: toPairs('pression'),
      indice_uv: toPairs('indice_uv'),
      co2: toPairs('co2'),
    };
  }, [data]);

  function MiniChart({ points, color, label }:{ points: {t:number; v:number; label?: string}[]; color:string; label:string }){
    const width = 600, height = 160, pad = 30;
    const [tooltip, setTooltip] = useState<{x: number, y: number, value: number, date: string} | null>(null);
    
    if (!points.length) return (
      <div className="card" style={{ 
        padding: 16, 
        border: '1px solid rgba(0,114,255,0.25)', 
        borderRadius: 12, 
        background: 'linear-gradient(180deg, rgba(8,12,18,0.8), rgba(6,10,16,0.8))',
        textAlign: 'center',
        height: 160,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'Rajdhani', sans-serif",
        letterSpacing: '0.03em',
        fontWeight: 300,
        opacity: 0.7
      }}>
        <div>Aucune donnée disponible pour {label}</div>
      </div>
    );
    
    const xs = points.map(p=>p.t), ys = points.map(p=>p.v);
    const xmin = Math.min(...xs), xmax = Math.max(...xs);
    const ymin = Math.min(...ys), ymax = Math.max(...ys);
    const yPadding = (ymax - ymin) * 0.1 || 1; // Add 10% padding or default to 1
    
    // Normalized coordinates with padding
    const normX = (t:number) => pad + (width-2*pad) * (xs.length === 1 ? 0.5 : (t - xmin) / (xmax - xmin || 1));
    const normY = (v:number) => height - pad - (height-2*pad) * ((v - (ymin - yPadding)) / ((ymax + yPadding) - (ymin - yPadding) || 1));
    
    // Create path data
    const d = points.map((p,i)=> `${i?'L':'M'}${normX(p.t)},${normY(p.v)}`).join(' ');
    
    // Create a lighter fill below the line for visual effect
    const areaPath = d + ` L${normX(points[points.length-1].t)},${height-pad} L${normX(points[0].t)},${height-pad} Z`;
    
    // Format date for axis labels
    const formatDate = (timestamp: number) => {
      const date = new Date(timestamp);
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    };
    
    // Calculate tick values for y-axis
    const yTicks = [ymin, (ymin + ymax) / 2, ymax].map(v => Math.round(v * 10) / 10);
    
    // Calculate tick values for x-axis (first, middle, last)
    const xTicks = [
      { value: xmin, label: formatDate(xmin) },
      { value: (xmin + xmax) / 2, label: formatDate((xmin + xmax) / 2) },
      { value: xmax, label: formatDate(xmax) }
    ];
    
    return (
      <div className="card" style={{ 
        padding: 16, 
        border: '1px solid rgba(0,114,255,0.25)', 
        borderRadius: 12, 
        background: 'linear-gradient(180deg, rgba(8,12,18,0.8), rgba(6,10,16,0.8))',
        boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ 
          marginBottom: 12, 
          opacity: 0.9, 
          fontWeight: 500, 
          fontSize: 16,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontFamily: "'Montserrat', sans-serif",
          letterSpacing: '0.03em',
          position: 'relative',
          zIndex: 1
        }}>
          <span>{label}</span>
          <span className="ds-mono" style={{ fontSize: 14, opacity: 0.7, color: color }}>
            {points.length} mesures • min: {Math.min(...ys).toFixed(1)} • max: {Math.max(...ys).toFixed(1)}
          </span>
        </div>
        
        <svg width={width} height={height} style={{ overflow: 'visible', position: 'relative', zIndex: 1 }}>
          {/* Grid lines */}
          {yTicks.map(tick => (
            <line 
              key={`y-${tick}`}
              x1={pad} 
              y1={normY(tick)} 
              x2={width-pad} 
              y2={normY(tick)} 
              stroke="rgba(255,255,255,0.1)" 
              strokeDasharray="4 4"
            />
          ))}
          
          {/* Y-axis labels */}
          {yTicks.map(tick => (
            <text 
              key={`y-label-${tick}`}
              x={pad - 8} 
              y={normY(tick)} 
              textAnchor="end" 
              dominantBaseline="middle"
              fill="rgba(255,255,255,0.6)"
              fontSize="11"
              fontFamily="'Rajdhani', sans-serif"
              fontWeight="300"
              letterSpacing="0.05em"
            >
              {tick}
            </text>
          ))}
          
          {/* X-axis labels */}
          {xTicks.map(tick => (
            <text 
              key={`x-label-${tick.value}`}
              x={normX(tick.value)} 
              y={height - pad + 14} 
              textAnchor="middle"
              fill="rgba(255,255,255,0.6)"
              fontSize="11"
              fontFamily="'Rajdhani', sans-serif"
              fontWeight="300"
              letterSpacing="0.05em"
            >
              {tick.label}
            </text>
          ))}
          
          {/* Area fill */}
          <path 
            d={areaPath} 
            fill={color} 
            fillOpacity="0.15" 
          />
          
          {/* Main line */}
          <path 
            d={d} 
            fill="none" 
            stroke={color} 
            strokeWidth={2.5}
            filter="drop-shadow(0 0 4px rgba(0,0,0,0.5))"
          />
          
          {/* Data points for hover */}
          {points.map((point, i) => (
            <circle
              key={i}
              cx={normX(point.t)}
              cy={normY(point.v)}
              r={4}
              fill={color}
              stroke="#0a0f14"
              strokeWidth={1.5}
              onMouseEnter={() => setTooltip({
                x: normX(point.t),
                y: normY(point.v),
                value: point.v,
                date: point.label || new Date(point.t).toLocaleString('fr-FR')
              })}
              onMouseLeave={() => setTooltip(null)}
              style={{ 
                cursor: 'pointer',
                transition: 'r 0.2s ease, fill 0.2s ease',
                filter: 'drop-shadow(0 0 3px rgba(0,0,0,0.5))'
              }}
            />
          ))}
          
          {/* Tooltip */}
          {tooltip && (
            <g>
              <rect
                x={tooltip.x - 90}
                y={tooltip.y - 50}
                width={180}
                height={42}
                rx={6}
                fill="rgba(0,20,40,0.95)"
                stroke={color}
                strokeWidth={1.5}
                filter="drop-shadow(0 4px 6px rgba(0,0,0,0.3))"
              />
              <text
                x={tooltip.x}
                y={tooltip.y - 31}
                textAnchor="middle"
                fill="white"
                fontSize="13"
                fontFamily="'Rajdhani', sans-serif"
                fontWeight="300"
                letterSpacing="0.05em"
              >
                {tooltip.value.toFixed(1)} | {tooltip.date}
              </text>
            </g>
          )}
        </svg>
        
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
    );
  }

  return (
    <main style={{ maxWidth: 1200, margin: '40px auto', padding: '0 20px' }}>
      <section style={{
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        background: 'linear-gradient(180deg, rgba(8,12,18,0.85), rgba(5,9,14,0.85))',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(0,114,255,0.25)',
        borderRadius: 16, 
        padding: '20px 24px', 
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
            fontFamily: "'Rajdhani', sans-serif"
          }}>Historique des données</h1>
          <div style={{ 
            opacity: 0.85, 
            marginTop: 8,
            fontFamily: "'Rajdhani', sans-serif",
            letterSpacing: '0.04em',
            fontWeight: 400
          }}>
            <span style={{ color: '#74e0c9', fontWeight: 700 }}>{data.length}</span> mesures • <span style={{ opacity: 0.9, color: '#74e0c9' }}>1 point tous les 10min</span> • Dernière mise à jour: <span style={{ fontWeight: 700 }}>{formatDateFR(data[0]?.created_at)}</span>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, position: 'relative', zIndex: 1 }}>
          <span style={{ 
            color: '#7bd0ff', 
            display: 'flex', 
            alignItems: 'center', 
            gap: 8,
            fontFamily: "'Share Tech Mono', 'Roboto Mono', monospace",
            letterSpacing: '0.03em',
            fontSize: 14
          }}>
            <span style={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              background: '#7bd0ff', 
              animation: 'blink 2s ease-in-out infinite',
              boxShadow: '0 0 8px rgba(123, 208, 255, 0.5)'
            }}></span>
            Mise à jour auto (60s)
          </span>
          {loading && <span style={{ 
            opacity: 0.6, 
            fontSize: 14,
            fontFamily: "'Roboto Mono', monospace"
          }}>          <span style={{ 
            opacity: 0.6, 
            fontSize: 14,
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: 300,
            letterSpacing: "0.05em"
          }}>(chargement…)</span></span>}
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

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 20 }}>
        <MiniChart points={series.temperature} color="#7bd0ff" label="Température (°C)" />
        <MiniChart points={series.humidite} color="#74e0c9" label="Humidité (%)" />
        <MiniChart points={series.pression} color="#b6a0ff" label="Pression (hPa)" />
        <MiniChart points={series.indice_uv} color="#ffd36e" label="Indice UV" />
        <MiniChart points={series.co2} color="#ff9ba1" label="CO2 (ppm)" />
      </div>

      <div style={{
        marginTop: 24,
        borderRadius: 16,
        border: '1px solid rgba(0,114,255,0.25)',
        overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.45)',
        background: 'linear-gradient(180deg, rgba(8,12,18,0.85), rgba(5,9,14,0.85))',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: 'linear-gradient(180deg, rgba(0,145,255,0.1), rgba(0,0,0,0))' }}>
            <tr>
              {['Date','Temp (°C)','Hum (%)','Press (hPa)','CO2 (ppm)','Hum surface (%)','Pluie','UV'].map(h => (
                <th key={h} style={{ 
                  textAlign: 'left', 
                  padding: '14px 16px', 
                  fontWeight: 500, 
                  opacity: 0.85,
                  fontFamily: "'Barlow Condensed', 'Rajdhani', sans-serif",
                  letterSpacing: '0.05em'
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.isArray(data) && data.length > 0 ? (
              // Afficher toutes les données dans le tableau (pas seulement les points filtrés)
              // L'utilisateur peut ainsi voir toutes les mesures en détail
              data.map((r:any) => (
                <tr key={r.id} style={{ 
                  borderTop: '1px solid rgba(255,255,255,0.06)', 
                  fontFamily: "'Rajdhani', sans-serif",
                  fontWeight: 300,
                  letterSpacing: '0.05em'
                }}>
                  <td style={{ padding: '12px 16px', opacity: 0.85 }}>{formatDateFR(r.created_at)}</td>
                  <td style={{ padding: '12px 16px' }}>{r.temperature?.toFixed?.(1) ?? '-'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.humidite?.toFixed?.(1) ?? '-'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.pression?.toFixed?.(1) ?? '-'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.co2?.toFixed?.(0) ?? '-'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.humidite_surface?.toFixed?.(1) ?? '-'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.pluie_detectee ? 'OUI' : 'NON'}</td>
                  <td style={{ padding: '12px 16px' }}>{r.indice_uv?.toFixed?.(1) ?? '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={8} style={{ 
                  padding: '20px', 
                  textAlign: 'center', 
                  opacity: 0.7,
                  fontFamily: "'Rajdhani', sans-serif",
                  fontWeight: 300,
                  letterSpacing: '0.05em'
                }}>
                  {loading ? 'Chargement des données...' : 'Aucune donnée disponible.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div style={{ marginTop: 16, textAlign: 'center' }}>
        <a 
          href="/" 
          style={{ 
            display: 'inline-block',
            margin: '20px auto',
            padding: '10px 24px', 
            background: 'linear-gradient(90deg, rgba(0,145,255,0.2), rgba(0,114,255,0.2))',
            border: '1px solid rgba(0,114,255,0.5)',
            borderRadius: 8,
            color: '#7bd0ff',
            textDecoration: 'none',
            fontWeight: 500,
            transition: 'all 0.2s ease',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            fontFamily: "'Rajdhani', sans-serif",
            letterSpacing: '0.05em'
          }}
        >
          ← Retour à l'accueil
        </a>
      </div>
      
      <style>{`
        @keyframes blink { 
          0%, 100% { opacity: 0.4; } 
          50% { opacity: 1; } 
        }
      `}</style>
    </main>
  );
}
