import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Filters from './components/Filters';
import './styles.css';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    cashiers: [],
    dateRange: { start: null, end: null },
    shifts: []
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://your-worker.your-subdomain.workers.dev/api/data');
      
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Memuat data dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={fetchData}>Coba Lagi</button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <h1 className="main-title">
          <span className="icon">📊</span>
          PPSA Analytics Dashboard
        </h1>
        <div className="store-name">
          <span className="icon">🏪</span>
          2GC6 BAROS PANDEGLANG
        </div>
        <p className="subtitle">
          Platform analytics komprehensif untuk monitoring real-time performa PPSA 
          dengan insights AI-powered untuk optimasi performa tim.
        </p>
      </header>

      <div className="dashboard-container">
        <aside className="sidebar">
          <Filters 
            data={data} 
            filters={filters} 
            onFiltersChange={setFilters} 
          />
        </aside>
        
        <main className="main-content">
          <Dashboard data={data} filters={filters} />
        </main>
      </div>
    </div>
  );
}

export default App;
