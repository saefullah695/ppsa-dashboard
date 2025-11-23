import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  LineChart, Line, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';

const Charts = ({ data, metrics }) => {
  // Component vs Target Chart Data
  const componentData = [
    { name: 'PSM', Actual: metrics.overallScores?.psm || 0, Target: 20 },
    { name: 'PWP', Actual: metrics.overallScores?.pwp || 0, Target: 25 },
    { name: 'SG', Actual: metrics.overallScores?.sg || 0, Target: 30 },
    { name: 'APC', Actual: metrics.overallScores?.apc || 0, Target: 25 },
  ];

  // Shift Performance Data
  const shiftData = metrics.shiftPerformance || [];

  // Cashier Performance Data (Top 10)
  const cashierData = (metrics.cashierPerformance || []).slice(0, 10);

  return (
    <div className="charts-section">
      <h2>📊 Performance Analytics</h2>
      
      <div className="charts-grid">
        {/* Component vs Target Chart */}
        <div className="chart-container">
          <h3>🎯 Component vs Target Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={componentData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Actual" fill="#667eea" name="Actual Score" />
              <Bar dataKey="Target" fill="#ef4444" name="Target" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Shift Performance Chart */}
        <div className="chart-container">
          <h3>🕐 Performance by Shift</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={shiftData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="avgScore" fill="#764ba2" name="Average Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Performers Chart */}
        <div className="chart-container">
          <h3>🏆 Top Performers</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={cashierData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={100} />
              <Tooltip />
              <Bar dataKey="avgScore" fill="#10b981" name="Average Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Trend Chart */}
        <div className="chart-container">
          <h3>📈 Daily Performance Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.dailyPerformance || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="avgScore" 
                stroke="#f093fb" 
                name="Daily Average"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Charts;
