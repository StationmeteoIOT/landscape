export const dynamic = 'force-dynamic';

async function fetchFromBackend() {
  const API_BASE = process.env.API_BASE || 'http://localhost:5000';
  const endpoints = [
    `${API_BASE}/measures?limit=100`,
    `${API_BASE}/mesures?limit=100`,
  ];
  for (const url of endpoints) {
    try {
      const res = await fetch(url, { cache: 'no-store' });
      if (!res.ok) continue;
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch {
      // try next endpoint
    }
  }
  return [];
}

export async function GET() {
  const data = await fetchFromBackend();
  return new Response(JSON.stringify(data), {
    headers: {
      'content-type': 'application/json',
      'cache-control': 'no-store',
    },
  });
}
