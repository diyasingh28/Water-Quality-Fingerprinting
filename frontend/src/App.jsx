import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import StationDetail from "./pages/StationDetail";
import ReportsPage from "./pages/ReportsPage";
import ActionCenterPage from "./pages/ActionCenterPage";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="app-header">
          <h1>Water Quality Fingerprinting</h1>
          <nav>
            <NavLink to="/" end className="nav-link">Dashboard</NavLink>
            <NavLink to="/reports" className="nav-link">Reports</NavLink>
            <NavLink to="/action-center" className="nav-link">Action Center</NavLink>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stations/:stationId" element={<StationDetail />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/action-center" element={<ActionCenterPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
