export function processData(rawData) {
  return rawData.map(row => {
    const processed = { ...row };
    
    // Process dates
    if (row.TANGGAL) {
      const date = new Date(row.TANGGAL);
      processed.TANGGAL = date.toISOString();
      processed.HARI = getDayName(date.getDay());
      processed.BULAN = getMonthName(date.getMonth());
    }
    
    // Process shift
    if (row.SHIFT) {
      const shiftMap = {
        '1': 'Shift 1 (Pagi)',
        '2': 'Shift 2 (Siang)', 
        '3': 'Shift 3 (Malam)'
      };
      processed.SHIFT = shiftMap[row.SHIFT] || 'Unknown';
    }
    
    // Process numeric values
    const numericFields = [
      'PSM Target', 'PSM Actual', 'BOBOT PSM',
      'PWP Target', 'PWP Actual', 'BOBOT PWP', 
      'SG Target', 'SG Actual', 'BOBOT SG',
      'APC Target', 'APC Actual', 'BOBOT APC',
      'TARGET TEBUS 2500', 'ACTUAL TEBUS 2500'
    ];
    
    numericFields.forEach(field => {
      if (row[field]) {
        processed[field] = parseFloat(row[field]) || 0;
      }
    });
    
    // Calculate ACV percentages
    processed['(%) PSM ACV'] = calculateACV(row['PSM Actual'], row['PSM Target']);
    processed['(%) PWP ACV'] = calculateACV(row['PWP Actual'], row['PWP Target']);
    processed['(%) SG ACV'] = calculateACV(row['SG Actual'], row['SG Target']);
    processed['(%) APC ACV'] = calculateACV(row['APC Actual'], row['APC Target']);
    processed['(%) ACV TEBUS 2500'] = calculateACV(row['ACTUAL TEBUS 2500'], row['TARGET TEBUS 2500']);
    
    // Calculate weighted scores
    const weights = { PSM: 20, PWP: 25, SG: 30, APC: 25 };
    processed['SCORE PSM'] = (processed['(%) PSM ACV'] * weights.PSM) / 100;
    processed['SCORE PWP'] = (processed['(%) PWP ACV'] * weights.PWP) / 100;
    processed['SCORE SG'] = (processed['(%) SG ACV'] * weights.SG) / 100;
    processed['SCORE APC'] = (processed['(%) APC ACV'] * weights.APC) / 100;
    
    // Calculate total score
    processed['TOTAL SCORE PPSA'] = 
      processed['SCORE PSM'] + 
      processed['SCORE PWP'] + 
      processed['SCORE SG'] + 
      processed['SCORE APC'];
    
    return processed;
  });
}

export function calculateMetrics(data) {
  if (!data.length) return {};
  
  const overallScores = calculateOverallPPSABreakdown(data);
  const cashierPerformance = calculateCashierPerformance(data);
  const shiftPerformance = calculateShiftPerformance(data);
  const dailyPerformance = calculateDailyPerformance(data);
  const insights = generateInsights(data, overallScores, cashierPerformance);
  
  return {
    overallScores,
    cashierPerformance,
    shiftPerformance,
    dailyPerformance,
    insights,
    teamMetrics: calculateTeamMetrics(data)
  };
}

function calculateACV(actual, target) {
  const actualNum = parseFloat(actual) || 0;
  const targetNum = parseFloat(target) || 0;
  return targetNum !== 0 ? (actualNum / targetNum) * 100 : 0;
}

function calculateOverallPPSABreakdown(data) {
  const weights = { PSM: 20, PWP: 25, SG: 30, APC: 25 };
  const scores = { total: 0, psm: 0, pwp: 0, sg: 0, apc: 0 };
  
  // PSM, PWP, SG - cumulative metrics
  ['PSM', 'PWP', 'SG'].forEach(comp => {
    const totalTarget = data.reduce((sum, row) => sum + (parseFloat(row[`${comp} Target`]) || 0), 0);
    const totalActual = data.reduce((sum, row) => sum + (parseFloat(row[`${comp} Actual`]) || 0), 0);
    if (totalTarget > 0) {
      const acv = (totalActual / totalTarget) * 100;
      scores[comp.toLowerCase()] = (acv * weights[comp]) / 100;
    }
  });
  
  // APC - average metrics
  const avgTargetAPC = data.reduce((sum, row) => sum + (parseFloat(row['APC Target']) || 0), 0) / data.length;
  const avgActualAPC = data.reduce((sum, row) => sum + (parseFloat(row['APC Actual']) || 0), 0) / data.length;
  if (avgTargetAPC > 0) {
    const acvAPC = (avgActualAPC / avgTargetAPC) * 100;
    scores.apc = (acvAPC * weights.APC) / 100;
  }
  
  scores.total = scores.psm + scores.pwp + scores.sg + scores.apc;
  return scores;
}

function calculateCashierPerformance(data) {
  // Implementation similar to Python version
  const cashiers = {};
  
  data.forEach(row => {
    if (!row['NAMA KASIR']) return;
    
    const cashier = row['NAMA KASIR'];
    if (!cashiers[cashier]) {
      cashiers[cashier] = {
        records: [],
        totalScore: 0
      };
    }
    
    cashiers[cashier].records.push(row);
    cashiers[cashier].totalScore += row['TOTAL SCORE PPSA'] || 0;
  });
  
  return Object.entries(cashiers).map(([name, info]) => ({
    name,
    avgScore: info.totalScore / info.records.length,
    recordCount: info.records.length,
    // Add more metrics as needed
  })).sort((a, b) => b.avgScore - a.avgScore);
}

function calculateShiftPerformance(data) {
  // Implementation for shift performance
  const shifts = {};
  
  data.forEach(row => {
    const shift = row.SHIFT || 'Unknown';
    if (!shifts[shift]) {
      shifts[shift] = {
        records: [],
        totalScore: 0
      };
    }
    
    shifts[shift].records.push(row);
    shifts[shift].totalScore += row['TOTAL SCORE PPSA'] || 0;
  });
  
  return Object.entries(shifts).map(([name, info]) => ({
    name,
    avgScore: info.totalScore / info.records.length,
    recordCount: info.records.length
  }));
}

function calculateDailyPerformance(data) {
  // Implementation for daily performance
  const days = {};
  
  data.forEach(row => {
    if (!row.TANGGAL) return;
    
    const date = new Date(row.TANGGAL).toDateString();
    if (!days[date]) {
      days[date] = {
        records: [],
        totalScore: 0,
        date: row.TANGGAL
      };
    }
    
    days[date].records.push(row);
    days[date].totalScore += row['TOTAL SCORE PPSA'] || 0;
  });
  
  return Object.entries(days).map(([date, info]) => ({
    date: info.date,
    avgScore: info.totalScore / info.records.length,
    recordCount: info.records.length,
    dayOfWeek: getDayName(new Date(info.date).getDay())
  })).sort((a, b) => new Date(a.date) - new Date(b.date));
}

function calculateTeamMetrics(data) {
  const totalRecords = data.length;
  const uniqueCashiers = new Set(data.map(row => row['NAMA KASIR']).filter(Boolean)).size;
  const scores = data.map(row => row['TOTAL SCORE PPSA'] || 0).filter(score => !isNaN(score));
  
  return {
    totalRecords,
    uniqueCashiers,
    avgScore: scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0,
    maxScore: scores.length ? Math.max(...scores) : 0,
    minScore: scores.length ? Math.min(...scores) : 0,
    achievementRate: scores.length ? (scores.filter(score => score >= 100).length / scores.length) * 100 : 0
  };
}

function generateInsights(data, overallScores, cashierPerformance) {
  const insights = [];
  
  // Overall performance insight
  if (overallScores.total >= 100) {
    insights.push({
      type: 'success',
      title: '🎉 Target Tercapai!',
      text: `Total PPSA Score ${overallScores.total.toFixed(1)} telah melampaui target 100.`
    });
  } else {
    const gap = 100 - overallScores.total;
    insights.push({
      type: 'warning',
      title: '⚠️ Gap Performa',
      text: `Masih kurang ${gap.toFixed(1)} poin untuk mencapai target.`
    });
  }
  
  // Top performer insight
  if (cashierPerformance.length > 0) {
    const topPerformer = cashierPerformance[0];
    insights.push({
      type: 'success',
      title: `🌟 Top Performer: ${topPerformer.name}`,
      text: `Dengan rata-rata score ${topPerformer.avgScore.toFixed(1)}`
    });
  }
  
  return insights;
}

function getDayName(dayIndex) {
  const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
  return days[dayIndex];
}

function getMonthName(monthIndex) {
  const months = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ];
  return months[monthIndex];
}
