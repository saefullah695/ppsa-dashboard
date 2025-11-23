import React from 'react';

const KPICard = ({ label, value, icon, color, subtitle }) => {
  return (
    <div className="kpi-card" style={{ borderLeftColor: color }}>
      <div className="kpi-header">
        <span className="kpi-icon">{icon}</span>
        <span className="kpi-label">{label}</span>
      </div>
      <div className="kpi-value" style={{ color }}>
        {value}
      </div>
      {subtitle && (
        <div className="kpi-subtitle">{subtitle}</div>
      )}
    </div>
  );
};

export default KPICard;
