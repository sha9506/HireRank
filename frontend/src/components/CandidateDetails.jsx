import { useState, useEffect } from 'react'
import { useLocation, useNavigate, useParams, Link } from 'react-router-dom'
import { getCandidate } from '../services/api'
import { FiArrowLeft, FiUser, FiBriefcase, FiMail, FiPhone, FiMapPin, FiAward, FiBook, FiTool, FiTrendingUp } from 'react-icons/fi'
import ProgressBar from './ProgressBar'
import LoadingSpinner from './LoadingSpinner'
import Header from './Header'
import './CandidateDetails.css'

function CandidateDetails() {
  const location = useLocation()
  const navigate = useNavigate()
  const { candidateId } = useParams()
  const [result, setResult] = useState(location.state?.result || null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // If we don't have result from navigation state and we have candidateId, fetch from API
    if (!result && candidateId) {
      fetchCandidateDetails()
    }
  }, [candidateId])

  const fetchCandidateDetails = async () => {
    try {
      setLoading(true)
      const data = await getCandidate(candidateId)
      setResult(data)
      setError(null)
    } catch (err) {
      setError('Failed to load candidate details')
      console.error('Error fetching candidate:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
        <div> <Header />
      <div className="candidate-details-container">
       
        <LoadingSpinner />
      </div> </div>
    )
  }

  if (error) {
    return (
        <div> <Header />
      <div className="candidate-details-container">
        <div className="no-data-message">
          <FiUser className="no-data-icon" />
          <h2>Error Loading Candidate</h2>
          <p>{error}</p>
          <Link to="/candidates" className="back-home-btn">
            <FiArrowLeft /> Back to Candidates List
          </Link>
        </div>
      </div> </div>
    )
  }

  if (!result) {
    return (
        <div> <Header />
      <div className="candidate-details-container">
        <CandidatesList/>
        <div className="no-data-message">
          <FiUser className="no-data-icon" />
          <h2>No Candidate Data</h2>
          <p>Please upload a resume to see analysis results</p>
          <Link to="/" className="back-home-btn">
            <FiArrowLeft /> Back to Home
          </Link>
        </div>
      </div>
        </div>
    )
  }

  const {
    candidate_name,
    job_title,
    match_score,
    skills_found,
    skills_missing,
    contact_info,
    summary,
    uploaded_at,
    resume_text,
    education,
    experience,
    awards,
    certifications
  } = result

  const handleBackToHome = () => {
    navigate('/candidates')
  }

  return (
    <div> <Header />
    <div className="candidate-details-container">
      {/* Header with Back Button */}
      <div className="details-header">
        <button onClick={handleBackToHome} className="back-button">
          <FiArrowLeft /> Back to Home
        </button>
        <div className="header-actions">
          <Link to="/leaderboard" className="view-leaderboard-btn">
            View Full Leaderboard
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="details-content">
        {/* Candidate Info Card */}
        <div className="info-card">
          <div className="candidate-header">
            <div className="candidate-avatar">
              <FiUser />
            </div>
            <div className="candidate-info">
              <h1 className="candidate-name">{candidate_name}</h1>
              <div className="candidate-meta">
                <span className="job-title-badge">
                  <FiBriefcase /> {job_title}
                </span>
                {uploaded_at && (
                  <span className="upload-date">
                    Analyzed {new Date(uploaded_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Contact Information */}
          {contact_info && (
            <div className="contact-section">
              <h3 className="section-title">Contact Information</h3>
              <div className="contact-grid">
                {contact_info.email && (
                  <div className="contact-item">
                    <FiMail className="contact-icon" />
                    <a href={`mailto:${contact_info.email}`} className="contact-link">
                      {contact_info.email}
                    </a>
                  </div>
                )}
                {contact_info.phone && (
                  <div className="contact-item">
                    <FiPhone className="contact-icon" />
                    <a href={`tel:${contact_info.phone}`} className="contact-link">
                      {contact_info.phone}
                    </a>
                  </div>
                )}
                {contact_info.location && (
                  <div className="contact-item">
                    <FiMapPin className="contact-icon" />
                    <span>{contact_info.location}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Match Score Card */}
        <div className="score-card">
          <div className="score-header">
            <FiAward className="score-icon" />
            <h2>Match Score</h2>
          </div>
          <div className="score-display">
            <div className="score-number">{match_score}%</div>
            <ProgressBar score={match_score} showLabel={false} />
          </div>
          <p className="score-description">
            {match_score >= 80 && "Excellent match! This candidate has strong alignment with the job requirements."}
            {match_score >= 60 && match_score < 80 && "Good match. This candidate has most of the required skills."}
            {match_score >= 40 && match_score < 60 && "Moderate match. Consider for interview if other factors are strong."}
            {match_score < 40 && "Low match. This candidate may need additional training or experience."}
          </p>
        </div>

        {/* Summary */}
        {summary && (
          <div className="summary-card">
            <h2 className="section-title">AI Analysis Summary</h2>
            <p className="summary-text">{summary}</p>
          </div>
        )}

        {/* Skills Grid */}
        <div className="skills-grid">
          {/* Skills Found */}
          <div className="skills-card skills-found-card">
            <h3 className="skills-title">
              <svg className="skills-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Skills Found ({skills_found?.length || 0})
            </h3>
            <div className="skills-list">
              {skills_found && skills_found.length > 0 ? (
                skills_found.map((skill, index) => (
                  <span key={index} className="skill-badge skill-found">
                    {skill}
                  </span>
                ))
              ) : (
                <p className="no-skills">No matching skills found</p>
              )}
            </div>
          </div>

          {/* Skills Missing */}
          <div className="skills-card skills-missing-card">
            <h3 className="skills-title">
              <svg className="skills-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Skills Missing ({skills_missing?.length || 0})
            </h3>
            <div className="skills-list">
              {skills_missing && skills_missing.length > 0 ? (
                skills_missing.map((skill, index) => (
                  <span key={index} className="skill-badge skill-missing">
                    {skill}
                  </span>
                ))
              ) : (
                <p className="no-skills">All required skills found!</p>
              )}
            </div>
          </div>
        </div>

        {/* Education Section */}
        {education && education.length > 0 && (
          <div className="detail-section">
            <h2 className="section-title-with-icon">
              <FiBook className="title-icon" />
              Education
            </h2>
            <div className="detail-items">
              {education.map((edu, index) => (
                <div key={index} className="detail-item">
                  <div className="detail-item-header">
                    <h4>{edu.degree || 'Degree'}</h4>
                    {edu.year && <span className="detail-date">{edu.year}</span>}
                  </div>
                  {edu.institution && <p className="detail-institution">{edu.institution}</p>}
                  {edu.description && <p className="detail-description">{edu.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Experience Section */}
        {experience && experience.length > 0 && (
          <div className="detail-section">
            <h2 className="section-title-with-icon">
              <FiBriefcase className="title-icon" />
              Work Experience
            </h2>
            <div className="detail-items">
              {experience.map((exp, index) => (
                <div key={index} className="detail-item">
                  <div className="detail-item-header">
                    <h4>{exp.title || exp.position || 'Position'}</h4>
                    {exp.duration && <span className="detail-date">{exp.duration}</span>}
                  </div>
                  {exp.company && <p className="detail-institution">{exp.company}</p>}
                  {exp.description && <p className="detail-description">{exp.description}</p>}
                  {exp.responsibilities && Array.isArray(exp.responsibilities) && (
                    <ul className="detail-list">
                      {exp.responsibilities.map((resp, idx) => (
                        <li key={idx}>{resp}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Certifications Section */}
        {certifications && certifications.length > 0 && (
          <div className="detail-section">
            <h2 className="section-title-with-icon">
              <FiAward className="title-icon" />
              Certifications
            </h2>
            <div className="certifications-grid">
              {certifications.map((cert, index) => (
                <div key={index} className="certification-badge">
                  <FiAward className="cert-icon" />
                  <div>
                    <h4>{cert.name || cert}</h4>
                    {cert.issuer && <p className="cert-issuer">{cert.issuer}</p>}
                    {cert.year && <p className="cert-year">{cert.year}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Awards Section */}
        {awards && awards.length > 0 && (
          <div className="detail-section">
            <h2 className="section-title-with-icon">
              <FiTrendingUp className="title-icon" />
              Awards & Achievements
            </h2>
            <div className="detail-items">
              {awards.map((award, index) => (
                <div key={index} className="detail-item">
                  <h4>{award.title || award}</h4>
                  {award.description && <p className="detail-description">{award.description}</p>}
                  {award.year && <span className="detail-date">{award.year}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button onClick={handleBackToHome} className="action-btn btn-secondary">
            Back to Candidates List
          </button>
          <Link to="/dashboard" className="action-btn btn-primary">
            View Leaderboard
          </Link>
        </div>
      </div>
    </div> </div>
  )
}

export default CandidateDetails
