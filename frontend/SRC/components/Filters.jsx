import React, { useMemo } from 'react';

const Filters = ({ data, filters, onFiltersChange }) => {
  const availableCashiers = useMemo(() => {
    if (!data?.rawData) return [];
    const cashiers = [...new Set(data.rawData.map(row => row['NAMA KASIR']).filter(Boolean))];
    return cashiers.sort();
  }, [data]);

  const availableShifts = useMemo(() => {
    if (!data?.rawData) return [];
    const shifts = [...new Set(data.rawData.map(row => row.SHIFT).filter(Boolean))];
    return shifts.sort();
  }, [data]);

  const handleCashierChange = (cashier) => {
    const newCashiers = filters.cashiers.includes(cashier)
      ? filters.cashiers.filter(c => c !== cashier)
      : [...filters.cashiers, cashier];
    
    onFiltersChange({
      ...filters,
      cashiers: newCashiers
    });
  };

  const handleShiftChange = (shift) => {
    const newShifts = filters.shifts.includes(shift)
      ? filters.shifts.filter(s => s !== shift)
      : [...filters.shifts, shift];
    
    onFiltersChange({
      ...filters,
      shifts: newShifts
    });
  };

  const handleDateChange = (type, value) => {
    onFiltersChange({
      ...filters,
      dateRange: {
        ...filters.dateRange,
        [type]: value ? new Date(value) : null
      }
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      cashiers: [],
      dateRange: { start: null, end: null },
      shifts: []
    });
  };

  return (
    <div className="filters-panel">
      <h3>⚙️ Filter & Pengaturan</h3>
      
      {/* Cashier Filter */}
      <div className="filter-group">
        <label>🧑‍💼 Pilih Kasir:</label>
        <div className="checkbox-group">
          {availableCashiers.map(cashier => (
            <label key={cashier} className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.cashiers.includes(cashier)}
                onChange={() => handleCashierChange(cashier)}
              />
              {cashier}
            </label>
          ))}
        </div>
      </div>

      {/* Shift Filter */}
      <div className="filter-group">
        <label>🕐 Pilih Shift:</label>
        <div className="checkbox-group">
          {availableShifts.map(shift => (
            <label key={shift} className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.shifts.includes(shift)}
                onChange={() => handleShiftChange(shift)}
              />
              {shift}
            </label>
          ))}
        </div>
      </div>

      {/* Date Range Filter */}
      <div className="filter-group">
        <label>📅 Rentang Tanggal:</label>
        <div className="date-inputs">
          <input
            type="date"
            placeholder="Dari tanggal"
            onChange={(e) => handleDateChange('start', e.target.value)}
          />
          <input
            type="date"
            placeholder="Sampai tanggal"
            onChange={(e) => handleDateChange('end', e.target.value)}
          />
        </div>
      </div>

      {/* Summary */}
      <div className="filter-summary">
        <h4>📊 Ringkasan Data</h4>
        <div className="summary-item">
          <strong>Total Records:</strong> {data?.rawData?.length || 0}
        </div>
        <div className="summary-item">
          <strong>Kasir Terpilih:</strong> {filters.cashiers.length}
        </div>
        <div className="summary-item">
          <strong>Avg Score:</strong> {data?.metrics?.overallScores?.total.toFixed(1) || '0'}
        </div>
      </div>

      <button className="clear-filters" onClick={clearFilters}>
        🗑️ Clear Filters
      </button>
    </div>
  );
};

export default Filters;
