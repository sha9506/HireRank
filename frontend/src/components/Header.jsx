import { useTheme } from '../context/ThemeContext'
import { Link, useLocation } from 'react-router-dom'
import { FiSun, FiMoon, FiHome, FiBarChart2, FiClock, FiUsers } from 'react-icons/fi'
import './Header.css'

function Header() {
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === path
    }
    return location.pathname.startsWith(path)
  }

  return (
    <header className="header-container">
      <div className="header-content">
        <div className="header-flex">
          <Link to="/" className="header-brand">
            <div className="header-logo">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="header-brand-text">
              <h1 className="header-title">HireRank</h1>
              <p className="header-subtitle">Talent Screening Platform</p>
            </div>
          </Link>

          <div className="header-actions">
            {/* Navigation Links */}
            <nav className="header-nav">
              <Link to="/" className={`header-nav-link ${isActive('/') && location.pathname === '/' ? 'active' : ''}`}>
                <FiHome className="nav-icon" />
                <span>Home</span>
              </Link>
              <Link to="/candidates" className={`header-nav-link ${isActive('/candidates') || isActive('/candidate-details') ? 'active' : ''}`}>
                <FiUsers className="nav-icon" />
                <span>Candidates</span>
              </Link>
              <Link to="/leaderboard" className={`header-nav-link ${isActive('/leaderboard') ? 'active' : ''}`}>
                <FiBarChart2 className="nav-icon" />
                <span>Leaderboard</span>
              </Link>
              <Link to="/history" className={`header-nav-link ${isActive('/history') ? 'active' : ''}`}>
                <FiClock className="nav-icon" />
                <span>History</span>
              </Link>
            </nav>

            {/* Theme Toggle */}
            <button onClick={toggleTheme} className="theme-toggle-btn" aria-label="Toggle theme">
              {theme === 'light' ? (
                <FiMoon className="theme-toggle-icon" />
              ) : (
                <FiSun className="theme-toggle-icon" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
