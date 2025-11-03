import React, { useState, useEffect } from 'react'
import { getTopPerformers } from '../../services/api'
import ProgressBar from '../Common/ProgressBar'
import { FiAward, FiStar } from 'react-icons/fi'
import './TopPerformers.css'

const TopPerformers = () => {
  const [performers, setPerformers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTopPerformers()
  }, [])

  const fetchTopPerformers = async () => {
    try {
      setLoading(true)
      const data = await getTopPerformers(3)
      setPerformers(data.top_performers || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching top performers:', err)
      setError('Failed to load top performers')
    } finally {
      setLoading(false)
    }
  }

  const getTrophyIcon = (index) => {
    if (index === 0) return <FiAward className="trophy-icon-svg gold" />
    if (index === 1) return <FiAward className="trophy-icon-svg silver" />
    if (index === 2) return <FiAward className="trophy-icon-svg bronze" />
    return <FiStar className="trophy-icon-svg" />
  }

  const getTrophyClass = (index) => {
    const classes = ['trophy-gold', 'trophy-silver', 'trophy-bronze']
    return classes[index] || ''
  }

  if (loading) {
    return (
      <div className="top-performers-loading">
        <div className="spinner"></div>
        <p>Loading top performers...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="top-performers-error">
        <p>{error}</p>
      </div>
    )
  }

  if (performers.length === 0) {
    return (
      <div className="top-performers-empty">
        <p>No candidates analyzed yet. Upload a resume to get started!</p>
      </div>
    )
  }

  return (
    <div className="top-performers-container">
      <div className="top-performers-header">
        <h2 className="top-performers-title">
          <FiAward className="header-icon" /> Top Performers
        </h2>
        <p className="top-performers-subtitle">
          Our highest-ranking candidates across all positions
        </p>
      </div>
      
      <div className="performers-grid">
        {performers.map((performer, index) => (
          <div key={performer._id} className={`performer-card ${getTrophyClass(index)}`}>
            <div className="performer-rank">
              <span className="trophy-icon">{getTrophyIcon(index)}</span>
              <span className="rank-number">#{index + 1}</span>
            </div>
            
            <div className="performer-info">
              <h3 className="performer-name">{performer.candidate_name}</h3>
              <p className="performer-title">{performer.job_title}</p>
            </div>
            
            <div className="performer-score">
              <ProgressBar score={performer.match_score} showLabel={false} height="16px" />
              <div className="score-details">
                <span className="score-value">{performer.match_score}%</span>
                <span className="score-label">Match Score</span>
              </div>
            </div>
            
            {performer.skills && performer.skills.length > 0 && (
              <div className="performer-skills">
                <span className="skills-label">Key Skills:</span>
                <div className="skills-tags">
                  {performer.skills.slice(0, 5).map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                  {performer.skills.length > 5 && (
                    <span className="skill-tag more">+{performer.skills.length - 5} more</span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default TopPerformers
