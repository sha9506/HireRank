import React, { useState, useEffect } from 'react'
import { getRankings, deleteCandidate, updateRemarks } from '../../services/api'
import ProgressBar from '../Common/ProgressBar'
import { FiTrash2 } from 'react-icons/fi'
import './Leaderboard.css'
import Header from '../Layout/Header'

const Leaderboard = () => {
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterJobTitle, setFilterJobTitle] = useState('')
  const [editingRemarks, setEditingRemarks] = useState(null)
  const [remarksValue, setRemarksValue] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    fetchRankings()
  }, [filterJobTitle])

  const fetchRankings = async () => {
    try {
      setLoading(true)
      const data = await getRankings(filterJobTitle || null)
      setRankings(data.rankings || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching rankings:', err)
      setError('Failed to load rankings')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateRemarks = async (candidateId) => {
    try {
      await updateRemarks(candidateId, remarksValue)
      // Update local state
      setRankings(rankings.map(r => 
        r._id === candidateId ? { ...r, remarks: remarksValue } : r
      ))
      setEditingRemarks(null)
      setRemarksValue('')
    } catch (err) {
      console.error('Error updating remarks:', err)
      alert('Failed to update remarks')
    }
  }

  const handleDelete = async (candidateId) => {
    try {
      await deleteCandidate(candidateId)
      setRankings(rankings.filter(r => r._id !== candidateId))
      setDeleteConfirm(null)
    } catch (err) {
      console.error('Error deleting candidate:', err)
      alert('Failed to delete candidate')
    }
  }

  const startEditRemarks = (candidate) => {
    setEditingRemarks(candidate._id)
    setRemarksValue(candidate.remarks || '')
  }

  const getJobTitles = () => {
    const titles = [...new Set(rankings.map(r => r.job_title))]
    return titles.sort()
  }

  if (loading) {
    return (
      <div className="leaderboard-loading">
        <div className="spinner-large"></div>
        <p>Loading leaderboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="leaderboard-error">
        <p>{error}</p>
        <button onClick={fetchRankings} className="retry-btn">Retry</button>
      </div>
    )
  }

  return (
    <div> <Header/>
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h1 className="leaderboard-title">Candidate Leaderboard</h1>
        <p className="leaderboard-subtitle">
          All candidates ranked by match score
        </p>
      </div>

      {/* Filters */}
      <div className="leaderboard-filters">
        <div className="filter-group">
          <label htmlFor="jobTitleFilter">Filter by Job Title:</label>
          <select
            id="jobTitleFilter"
            value={filterJobTitle}
            onChange={(e) => setFilterJobTitle(e.target.value)}
            className="filter-select"
          >
            <option value="">All Positions</option>
            {getJobTitles().map(title => (
              <option key={title} value={title}>{title}</option>
            ))}
          </select>
        </div>
        
        <div className="results-count">
          {rankings.length} candidate{rankings.length !== 1 ? 's' : ''} found
        </div>
      </div>

      {/* Leaderboard Table */}
      {rankings.length === 0 ? (
        <div className="no-results">
          <p>No candidates found. Upload a resume to get started!</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Job Title</th>
                <th>Match Score</th>
                <th>Skills</th>
                <th>Remarks</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((candidate, index) => (
                <tr key={candidate._id} className="candidate-row">
                  <td className="rank-cell">
                    <span className="rank-badge">{index + 1}</span>
                  </td>
                  <td className="name-cell">
                    <div className="candidate-name">{candidate.candidate_name}</div>
                    <div className="candidate-email">{candidate.candidate_info?.email}</div>
                  </td>
                  <td className="job-cell">{candidate.job_title}</td>
                  <td className="score-cell">
                    <ProgressBar score={candidate.match_score} showLabel={false} />
                    <span className="score-value">{candidate.match_score}%</span>
                  </td>
                  <td className="skills-cell">
                    <div className="skills-list">
                      {candidate.skills.slice(0, 3).map((skill, idx) => (
                        <span key={idx} className="skill-badge">{skill}</span>
                      ))}
                      {candidate.skills.length > 3 && (
                        <span className="skill-badge more">+{candidate.skills.length - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="remarks-cell">
                    {editingRemarks === candidate._id ? (
                      <div className="remarks-edit">
                        <textarea
                          value={remarksValue}
                          onChange={(e) => setRemarksValue(e.target.value)}
                          className="remarks-textarea"
                          placeholder="Add remarks..."
                        />
                        <div className="remarks-actions">
                          <button
                            onClick={() => handleUpdateRemarks(candidate._id)}
                            className="save-btn"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingRemarks(null)}
                            className="cancel-btn"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div
                        className="remarks-display"
                        onClick={() => startEditRemarks(candidate)}
                      >
                        {candidate.remarks || 'Click to add remarks...'}
                      </div>
                    )}
                  </td>
                  <td className="actions-cell">
                    <button
                      onClick={() => setDeleteConfirm(candidate._id)}
                      className="delete-btn"
                      title="Delete candidate"
                    >
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Deletion</h3>
            <p>Are you sure you want to delete this candidate? This action cannot be undone.</p>
            <div className="modal-actions">
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="confirm-delete-btn"
              >
                Delete
              </button>
              <button
                onClick={() => setDeleteConfirm(null)}
                className="cancel-modal-btn"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  )
}

export default Leaderboard
