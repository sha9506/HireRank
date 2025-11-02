import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import UploadSection from './components/UploadSection'
import ResultsSection from './components/ResultsSection'
import LoadingSpinner from './components/LoadingSpinner'
import TopPerformers from './components/TopPerformers'
import Dashboard from './components/Dashboard'
import Leaderboard from './components/Leaderboard'
import History from './components/History'
import CandidateDetails from './components/CandidateDetails'
import CandidatesList from './components/CandidatesList'
import AnalyzingPage from './components/AnalyzingPage'
import { ThemeProvider } from './context/ThemeContext'
import './App.css'

function HomePage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalysisComplete = (data) => {
    setResult(data)
    setError(null)
  }

  const handleAnalysisStart = () => {
    setLoading(true)
    setError(null)
    setResult(null)
  }

  const handleAnalysisEnd = () => {
    setLoading(false)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setLoading(false)
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setLoading(false)
  }

  return (
    <div className="app-container">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="hero-title">HireRank</h1>
          <p className="hero-subtitle">
            AI-Powered Resume Ranking & Talent Screening Platform
          </p>
          <p className="hero-description">
            Upload resumes and get instant AI-driven insights on candidate fit
          </p>
        </div>

        {/* Top Performers Section */}
        <TopPerformers />

        {/* Error Display */}
        {error && (
          <div className="error-alert">
            <div className="flex-shrink-0">
              <svg className="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="error-content">
              <h3 className="error-title">Analysis Error</h3>
              <p className="error-message">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="error-close-btn">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <UploadSection
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisStart={handleAnalysisStart}
              onAnalysisEnd={handleAnalysisEnd}
              onError={handleError}
              disabled={loading}
            />
          </div>

          {/* Results Section */}
          <div className="lg:col-span-1">
            {loading ? (
              <LoadingSpinner />
            ) : result ? (
              <ResultsSection result={result} onReset={handleReset} />
            ) : (
              <div className="empty-state">
                <svg className="empty-state-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="empty-state-title">No Analysis Yet</h3>
                <p className="empty-state-text">Upload a resume and job title to get started</p>
              </div>
            )}
          </div>
        </div>

        {/* Features Section */}
        <div className="feature-cards">
          <div className="feature-card">
            <div className="feature-icon-wrapper feature-icon-primary">
              <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="feature-title">AI-Powered Analysis</h3>
            <p className="feature-description">
              Advanced NLP models analyze resumes with semantic understanding
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon-wrapper feature-icon-purple">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="feature-title">Instant Ranking</h3>
            <p className="feature-description">
              Get immediate match scores and detailed skill extraction
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon-wrapper feature-icon-green">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="feature-title">Smart Insights</h3>
            <p className="feature-description">
              Receive AI-generated summaries explaining candidate fit
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>HireRank &copy; 2025 - AI-Powered Talent Screening Platform</p>
          <p>Built with React, FastAPI, and HuggingFace Transformers</p>
        </div>
      </footer>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/candidates" element={<CandidatesList />} />
          <Route path="/candidates-details" element={<CandidateDetails />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
