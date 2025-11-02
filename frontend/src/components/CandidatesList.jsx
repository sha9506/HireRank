import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getHistory } from '../services/api'
import { FiUser, FiSearch, FiBriefcase, FiCalendar, FiChevronRight } from 'react-icons/fi'
import ProgressBar from './ProgressBar'
import LoadingSpinner from './LoadingSpinner'
import Header from './Header'
import './CandidatesList.css'

function CandidatesList() {
  const [candidates, setCandidates] = useState([])
  const [filteredCandidates, setFilteredCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedJobTitle, setSelectedJobTitle] = useState('all')
  const navigate = useNavigate()

  useEffect(() => {
    fetchCandidates()
  }, [])

  useEffect(() => {
    filterCandidates()
  }, [searchTerm, selectedJobTitle, candidates])

  const fetchCandidates = async () => {
    try {
      setLoading(true)
      const data = await getHistory(1000) // Get all candidates
      console.log('Fetched candidates:', data)
      // Check if data is in the correct format
      const candidatesList = data.history || data || []
      setCandidates(candidatesList)
      setFilteredCandidates(candidatesList)
      setError(null)
    } catch (err) {
      setError('Failed to load candidates')
      console.error('Error fetching candidates:', err)
    } finally {
      setLoading(false)
    }
  }

  const filterCandidates = () => {
    let filtered = candidates

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(candidate =>
        candidate.candidate_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        candidate.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        candidate.contact_info?.email?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by job title
    if (selectedJobTitle !== 'all') {
      filtered = filtered.filter(candidate => candidate.job_title === selectedJobTitle)
    }

    setFilteredCandidates(filtered)
  }

  const handleCandidateClick = (candidate) => {
    navigate('/candidates-details', { state: { result: candidate } })
  }

  const getUniqueJobTitles = () => {
    const titles = [...new Set(candidates.map(c => c.job_title).filter(Boolean))]
    return titles.sort()
  }

  if (loading) {
    return (
      <div> <Header />
      <div className="candidates-list-container">
        
        <LoadingSpinner />
      </div> </div>
    )
  }

  if (error) {
    return (
      <div> <Header />
      <div className="candidates-list-container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchCandidates} className="retry-btn">Retry</button>
        </div>
      </div> </div>
    )
  }

  return (
    <div> <Header />
    <div className="candidates-list-container">
      <div className="candidates-list-header">
        <div className="header-title-section">
          <h1 className="page-title">All Candidates</h1>
          <p className="page-subtitle">View and manage all candidate profiles</p>
        </div>
        <div className="candidates-count">
          <span className="count-badge">{filteredCandidates.length}</span>
          <span className="count-label">Candidates</span>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by name, job title, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">Job Title:</label>
          <select
            value={selectedJobTitle}
            onChange={(e) => setSelectedJobTitle(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Positions</option>
            {getUniqueJobTitles().map(title => (
              <option key={title} value={title}>{title}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Candidates Grid */}
      {filteredCandidates.length === 0 ? (
        <div className="no-candidates">
          <FiUser className="no-candidates-icon" />
          <h3>No Candidates Found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="candidates-grid">
          {filteredCandidates.map((candidate) => (
            <div
              key={candidate._id}
              className="candidate-card"
              onClick={() => handleCandidateClick(candidate)}
            >
              <div className="candidate-card-header">
                <div className="candidate-avatar">
                  <FiUser />
                </div>
                <div className="candidate-info">
                  <h3 className="candidate-name">{candidate.candidate_name || 'Unknown'}</h3>
                  <div className="candidate-job-title">
                    <FiBriefcase className="icon" />
                    <span>{candidate.job_title}</span>
                  </div>
                </div>
              </div>

              <div className="candidate-card-body">
                {/* Match Score */}
                <div className="score-section">
                  <div className="score-label">Match Score</div>
                  <div className="score-value">{candidate.match_score}%</div>
                  <ProgressBar score={candidate.match_score} showLabel={false} />
                </div>

                {/* Contact Info */}
                {(candidate.contact_info || candidate.candidate_info) && (
                  <div className="contact-info-preview">
                    {(candidate.contact_info?.email || candidate.candidate_info?.email) && (
                      <div className="contact-item-small">
                        <span className="contact-text">{candidate.contact_info?.email || candidate.candidate_info?.email}</span>
                      </div>
                    )}
                    {(candidate.contact_info?.phone || candidate.candidate_info?.phone) && (
                      <div className="contact-item-small">
                        <span className="contact-text">{candidate.contact_info?.phone || candidate.candidate_info?.phone}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Skills Preview */}
                {(candidate.skills || candidate.skills_found) && (candidate.skills || candidate.skills_found).length > 0 && (
                  <div className="skills-preview">
                    <div className="skills-label">Skills:</div>
                    <div className="skills-tags">
                      {(candidate.skills || candidate.skills_found).slice(0, 3).map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                      {(candidate.skills || candidate.skills_found).length > 3 && (
                        <span className="skill-tag more">+{(candidate.skills || candidate.skills_found).length - 3}</span>
                      )}
                    </div>
                  </div>
                )}

                {/* Date */}
                <div className="candidate-date">
                  <FiCalendar className="icon" />
                  <span>Analyzed {new Date(candidate.uploaded_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="candidate-card-footer">
                <button className="view-details-btn">
                  View Full Profile
                  <FiChevronRight />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div> </div>
  )
}

export default CandidatesList
