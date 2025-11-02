import React from 'react'
import './ProgressBar.css'

const ProgressBar = ({ score, showLabel = true, height = '12px' }) => {
  const getColorClass = (score) => {
    if (score >= 80) return 'progress-excellent'
    if (score >= 60) return 'progress-good'
    if (score >= 40) return 'progress-moderate'
    return 'progress-low'
  }

  const getScoreText = (score) => {
    if (score >= 80) return 'Excellent Match'
    if (score >= 60) return 'Good Match'
    if (score >= 40) return 'Moderate Match'
    return 'Needs Review'
  }

  return (
    <div className="progress-bar-container">
      {showLabel && (
        <div className="progress-label">
          <span className="progress-score">{score}%</span>
          <span className="progress-text">{getScoreText(score)}</span>
        </div>
      )}
      <div className="progress-bar-wrapper" style={{ height }}>
        <div
          className={`progress-bar-fill ${getColorClass(score)}`}
          style={{ width: `${score}%` }}
        >
          {!showLabel && <span className="progress-inline-text">{score}%</span>}
        </div>
      </div>
    </div>
  )
}

export default ProgressBar
