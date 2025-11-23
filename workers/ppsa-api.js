export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const url = new URL(request.url);
      const path = url.pathname;

      if (path === '/api/data' || path === '/api/data/') {
        return await handleDataRequest(env);
      }

      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};

async function handleDataRequest(env) {
  try {
    // Simulate data processing - replace with actual Google Sheets integration
    const mockData = generateMockData();
    
    return new Response(JSON.stringify({
      success: true,
      data: mockData,
      timestamp: new Date().toISOString()
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

function generateMockData() {
  const cashiers = ['Budi Santoso', 'Siti Rahayu', 'Ahmad Wijaya', 'Maya Sari', 'Rizki Pratama'];
  const shifts = ['Shift 1 (Pagi)', 'Shift 2 (Siang)', 'Shift 3 (Malam)'];
  const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
  
  const data = [];
  const startDate = new Date('2024-01-01');
  
  for (let i = 0; i < 100; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    data.push({
      TANGGAL: date.toISOString().split('T')[0],
      HARI: days[date.getDay()],
      SHIFT: shifts[Math.floor(Math.random() * shifts.length)],
      'NAMA KASIR': cashiers[Math.floor(Math.random() * cashiers.length)],
      'PSM Target': 100,
      'PSM Actual': 80 + Math.random() * 40,
      'BOBOT PSM': 20,
      'PWP Target': 100,
      'PWP Actual': 75 + Math.random() * 50,
      'BOBOT PWP': 25,
      'SG Target': 100,
      'SG Actual': 85 + Math.random() * 30,
      'BOBOT SG': 30,
      'APC Target': 100,
      'APC Actual': 90 + Math.random() * 20,
      'BOBOT APC': 25,
      'TARGET TEBUS 2500': 100,
      'ACTUAL TEBUS 2500': 70 + Math.random() * 60
    });
  }
  
  return data;
}
