import React from 'react'
import './Dashboard.css'

const Dashboard = ({ children }) => {
  return (
    <div className="dashboard-layout">
      <main className="dashboard-content">
        {children}
      </main>
    </div>
  )
}

export default Dashboard
