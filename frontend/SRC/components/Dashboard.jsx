import React, { useMemo } from 'react';
import KPICard from './KPICard';
import Charts from './Charts';

const Dashboard = ({ data, filters }) => {
  const filteredData = useMemo(() => {
    if (!data?.rawData) return [];
    
    let filtered = [...data.rawData];
    
    // Apply cashier filter
    if (filters.cashiers.length > 0) {
      filtered = filtered.filter(row => 
        filters.cashiers.includes(row['NAMA KASIR'])
      );
    }
    
    // Apply shift filter
    if (filters.shifts.length > 0) {
      filtered = filtered.filter(row => 
        filters.shifts.includes(row.SHIFT)
      );
    }
    
    // Apply date filter
    if (filters.dateRange.start && filters.dateRange.end) {
      filtered = filtered.filter(row => {
        const rowDate = new Date(row.TANGGAL);
        return rowDate >= filters.dateRange.start && rowDate <= filters.dateRange.end;
      });
    }
    
    return filtered;
  }, [data, filters]);

  const filteredMetrics = useMemo(() => {
    if (filteredData.length === 0) return data?.metrics || {};
    
    // Recalculate metrics for filtered data
    // This is a simplified version - you might want to implement full recalculation
    return data.metrics;
  }, [filteredData, data?.metrics]);

  if (!data) return null;

  return (
    <div className="dashboard">
      {/* Overall Performance Section */}
      <section className="performance-section">
        <h2>📈 Performance Overview</h2>
        
        <div className="kpi-grid">
          <KPICard
            label="Total PPSA Score"
            value={filteredMetrics.overallScores?.total.toFixed(1)}
            icon="🏆"
            color="#667eea"
            subtitle={`Gap: ${(filteredMetrics.overallScores?.total - 100).toFixed(1)}`}
          />
          
          <KPICard
            label="PSM Score"
            value={filteredMetrics.overallScores?.psm.toFixed(1)}
            icon="🛡️"
            color="#10b981"
            subtitle="Target: 20"
          />
          
          <KPICard
            label="PWP Score"
            value={filteredMetrics.overallScores?.pwp.toFixed(1)}
            icon="🛒"
            color="#f59e0b"
            subtitle="Target: 25"
          />
          
          <KPICard
            label="SG Score"
            value={filteredMetrics.overallScores?.sg.toFixed(1)}
            icon="⭐"
            color="#ef4444"
            subtitle="Target: 30"
          />
          
          <KPICard
            label="APC Score"
            value={filteredMetrics.overallScores?.apc.toFixed(1)}
            icon="📊"
            color="#8b5cf6"
            subtitle="Target: 25"
          />
        </div>
      </section>

      {/* Insights Section */}
      <section className="insights-section">
        <h2>🤖 AI-Powered Insights</h2>
        <div className="insights-grid">
          {filteredMetrics.insights?.map((insight, index) => (
            <div key={index} className={`insight-card ${insight.type}`}>
              <div className="insight-title">{insight.title}</div>
              <div className="insight-text">{insight.text}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Charts Section */}
      <Charts data={filteredData} metrics={filteredMetrics} />

      {/* Top Performers */}
      <section className="performers-section">
        <h2>🏅 Top Performers</h2>
        <div className="performers-grid">
          {filteredMetrics.cashierPerformance?.slice(0, 3).map((cashier, index) => (
            <div key={cashier.name} className="performer-card">
              <div className="medal">
                {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
              </div>
              <h3>{cashier.name}</h3>
              <div className="score">{cashier.avgScore.toFixed(1)}</div>
              <div className="records">{cashier.recordCount} records</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
