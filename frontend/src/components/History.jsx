import React, { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import ProgressBar from './ProgressBar'
import './History.css'
import Header from './Header'

const History = () => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('date') // 'date' or 'score'

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const data = await getHistory()
      setHistory(data.history || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching history:', err)
      setError('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getFilteredAndSortedHistory = () => {
    let filtered = history

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (item) =>
          item.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.job_title.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.uploaded_at) - new Date(a.uploaded_at)
      } else {
        return b.match_score - a.match_score
      }
    })

    return sorted
  }

  const filteredHistory = getFilteredAndSortedHistory()

  if (loading) {
    return (
      <div className="history-loading">
        <div className="spinner-large"></div>
        <p>Loading history...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="history-error">
        <p>{error}</p>
        <button onClick={fetchHistory} className="retry-btn">Retry</button>
      </div>
    )
  }

  return (
    <div>
      <Header/>
    <div className="history-container">
        
      <div className="history-header">
        <h1 className="history-title">📜 Analysis History</h1>
        <p className="history-subtitle">
          Complete chronological record of all resume analyses
        </p>
      </div>

      {/* Search and Sort Controls */}
      <div className="history-controls">
        <div className="search-box">
          <svg
            className="search-icon"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search by name or job title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="sort-controls">
          <label htmlFor="sortBy">Sort by:</label>
          <select
            id="sortBy"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="date">Date (Newest First)</option>
            <option value="score">Score (Highest First)</option>
          </select>
        </div>
      </div>

      {/* History Grid */}
      {filteredHistory.length === 0 ? (
        <div className="no-results">
          <p>
            {searchTerm
              ? 'No results found. Try a different search term.'
              : 'No analysis history yet. Upload a resume to get started!'}
          </p>
        </div>
      ) : (
        <div className="history-grid">
          {filteredHistory.map((item) => (
            <div key={item._id} className="history-card">
              <div className="card-header">
                <div className="candidate-info">
                  <h3 className="candidate-name">{item.candidate_name}</h3>
                  <p className="job-title">{item.job_title}</p>
                </div>
                <div className="score-badge-container">
                  <div className="score-badge">{item.match_score}%</div>
                </div>
              </div>

              <div className="card-body">
                <div className="progress-section">
                  <ProgressBar score={item.match_score} showLabel={false} />
                </div>

                {item.skills && item.skills.length > 0 && (
                  <div className="skills-section">
                    <h4 className="section-title">Skills Identified</h4>
                    <div className="skills-tags">
                      {item.skills.slice(0, 6).map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                      {item.skills.length > 6 && (
                        <span className="skill-tag more">+{item.skills.length - 6}</span>
                      )}
                    </div>
                  </div>
                )}

                {item.summary && (
                  <div className="summary-section">
                    <h4 className="section-title">Analysis Summary</h4>
                    <p className="summary-text">{item.summary}</p>
                  </div>
                )}

                {item.candidate_info && (
                  <div className="contact-section">
                    <h4 className="section-title">Contact Info</h4>
                    <div className="contact-details">
                      {item.candidate_info.email && (
                        <div className="contact-item">
                          <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          <span>{item.candidate_info.email}</span>
                        </div>
                      )}
                      {item.candidate_info.phone && item.candidate_info.phone !== "Not found" && (
                        <div className="contact-item">
                          <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                          </svg>
                          <span>{item.candidate_info.phone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {item.remarks && (
                  <div className="remarks-section">
                    <h4 className="section-title">HR Remarks</h4>
                    <p className="remarks-text">{item.remarks}</p>
                  </div>
                )}
              </div>

              <div className="card-footer">
                <div className="footer-info">
                  <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{formatDate(item.uploaded_at)}</span>
                </div>
                <div className="footer-info">
                  <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>{item.resume_filename}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
    </div>
  )
}

export default History
