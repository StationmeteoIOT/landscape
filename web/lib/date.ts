export function parseCreatedAt(input?: string): Date | null {
  if (!input || typeof input !== 'string') return null;
  
  try {
    // Accept forms like 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS(.ms)Z?'
    // Prefer manual parsing to avoid cross-browser Invalid Date.
    const isoLike = input.replace(' ', 'T');
    
    // If includes 'T' and optional 'Z', try Date.parse first
    const tryIso = Date.parse(isoLike);
    if (!Number.isNaN(tryIso)) return new Date(tryIso);
  
    // Manual parse for 'YYYY-MM-DD HH:MM:SS'
    const m = input.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/);
    if (m) {
      const [_, y, mo, d, h, mi, s] = m;
      // Note: MySQL dates are in UTC, so we create a UTC date then convert to local
      const dt = new Date(Date.UTC(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi), Number(s)));
      return dt;
    }
    
    // Last resort: try to handle any other format
    const fallback = new Date(input);
    if (!isNaN(fallback.getTime())) {
      return fallback;
    }
  } catch (e) {
    console.error('Error parsing date:', input, e);
  }
  
  console.error('Failed to parse date:', input);
  return null;
}

export function formatDateFR(input?: string): string {
  const d = parseCreatedAt(input);
  if (!d) return '—';
  
  // Vérifier si la date est valide
  if (isNaN(d.getTime())) {
    console.warn('Invalid date detected:', input);
    return 'Date invalide';
  }
  
  try {
    return new Intl.DateTimeFormat('fr-FR', {
      dateStyle: 'short', 
      timeStyle: 'medium'
    }).format(d);
  } catch (e) {
    console.error('Error formatting date:', input, e);
    return d.toLocaleString('fr-FR');
  }
}

// Formate uniquement l'heure d'une date
export function formatTimeFR(input?: string): string {
  const d = parseCreatedAt(input);
  if (!d || isNaN(d.getTime())) return '—';
  
  try {
    return new Intl.DateTimeFormat('fr-FR', {
      timeStyle: 'medium'
    }).format(d);
  } catch (e) {
    console.error('Error formatting time:', input, e);
    return d.toLocaleTimeString('fr-FR');
  }
}

// Formate uniquement la date (sans l'heure)
export function formatDateOnlyFR(input?: string): string {
  const d = parseCreatedAt(input);
  if (!d || isNaN(d.getTime())) return '—';
  
  try {
    return new Intl.DateTimeFormat('fr-FR', {
      dateStyle: 'full'
    }).format(d);
  } catch (e) {
    console.error('Error formatting date only:', input, e);
    return d.toLocaleDateString('fr-FR');
  }
}
