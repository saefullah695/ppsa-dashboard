import { GoogleSpreadsheet } from 'google-spreadsheet';
import { calculateMetrics, processData } from './utils.js';

export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders,
      });
    }

    try {
      const url = new URL(request.url);
      
      if (url.pathname === '/api/data') {
        const data = await fetchDataFromGoogleSheets(env);
        return new Response(JSON.stringify(data), {
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders,
          },
        });
      }

      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders,
        },
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders,
        },
      });
    }
  },
};

async function fetchDataFromGoogleSheets(env) {
  const doc = new GoogleSpreadsheet(env.GOOGLE_SHEET_ID);

  await doc.useServiceAccountAuth({
    client_email: env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    private_key: env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
  });

  await doc.loadInfo();
  const sheet = doc.sheetsByIndex[0];
  const rows = await sheet.getRows();
  
  const rawData = rows.map(row => {
    const obj = {};
    sheet.headerValues.forEach(header => {
      obj[header] = row[header];
    });
    return obj;
  });

  const processedData = processData(rawData);
  const metrics = calculateMetrics(processedData);
  
  return {
    rawData: processedData,
    metrics,
    timestamp: new Date().toISOString()
  };
}
