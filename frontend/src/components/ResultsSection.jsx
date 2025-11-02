import { FiCheckCircle, FiUser, FiMail, FiPhone, FiBookOpen, FiBriefcase } from 'react-icons/fi'
import './ResultsSection.css'

function ResultsSection({ result, onReset }) {
  const getScoreClass = (score) => {
    if (score >= 80) return 'excellent'
    if (score >= 60) return 'good'
    if (score >= 40) return 'moderate'
    return 'low'
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match'
    if (score >= 60) return 'Good Match'
    if (score >= 40) return 'Moderate Match'
    return 'Needs Review'
  }

  return (
    <div className="results-container">
      {/* Match Score Card */}
      <div className={`score-card ${getScoreClass(result.match_score)}`}>
        <div className="score-card-content">
          <div className="score-badge">
            <span className="score-value">{result.match_score}%</span>
          </div>
          <h3 className="score-label">{getScoreLabel(result.match_score)}</h3>
          <p className="score-filename">{result.resume_filename}</p>
        </div>
      </div>

      {/* Candidate Information */}
      {result.candidate_info && (
        <div className="info-card">
          <h3 className="info-card-header">
            <FiUser />
            Candidate Information
          </h3>
          <div className="info-card-body">
            {result.candidate_info.name && result.candidate_info.name !== 'Not found' && (
              <div className="info-item">
                <FiUser className="info-icon" />
                <div>
                  <p className="info-label">Name</p>
                  <p className="info-value">{result.candidate_info.name}</p>
                </div>
              </div>
            )}
            
            {result.candidate_info.email && result.candidate_info.email !== 'Not found' && (
              <div className="info-item">
                <FiMail className="info-icon" />
                <div>
                  <p className="info-label">Email</p>
                  <p className="info-value">{result.candidate_info.email}</p>
                </div>
              </div>
            )}
            
            {result.candidate_info.phone && result.candidate_info.phone !== 'Not found' && (
              <div className="info-item">
                <FiPhone className="info-icon" />
                <div>
                  <p className="info-label">Phone</p>
                  <p className="info-value">{result.candidate_info.phone}</p>
                </div>
              </div>
            )}
            
            {result.candidate_info.education && result.candidate_info.education !== 'Not specified' && (
              <div className="info-item">
                <FiBookOpen className="info-icon" />
                <div>
                  <p className="info-label">Education</p>
                  <p className="info-value">{result.candidate_info.education}</p>
                </div>
              </div>
            )}
            
            {result.candidate_info.experience_years && result.candidate_info.experience_years !== 'Not specified' && (
              <div className="info-item">
                <FiBriefcase className="info-icon" />
                <div>
                  <p className="info-label">Experience</p>
                  <p className="info-value">{result.candidate_info.experience_years}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Summary */}
      <div className="summary-card">
        <h3 className="summary-header">
          <FiCheckCircle />
          AI Analysis Summary
        </h3>
        <p className="summary-text">{result.summary}</p>
      </div>

      {/* Skills Extracted */}
      <div className="skills-card">
        <h3 className="skills-header">
          Extracted Skills ({result.skills_extracted.length})
        </h3>
        {result.skills_extracted.length > 0 ? (
          <div className="skills-list">
            {result.skills_extracted.map((skill, index) => (
              <span key={index} className="skill-tag">{skill}</span>
            ))}
          </div>
        ) : (
          <p className="no-skills">
            No specific skills were identified in the resume.
          </p>
        )}
      </div>

      {/* Metadata */}
      <div className="metadata-card">
        <div className="metadata-content">
          <span>Analysis ID: {result.analysis_id}</span>
          <span>{new Date(result.processed_at).toLocaleString()}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button onClick={onReset} className="btn-secondary">
          Analyze Another Resume
        </button>
        <button onClick={() => window.print()} className="btn-primary">
          Export Results
        </button>
      </div>
    </div>
  )
}

export default ResultsSection
