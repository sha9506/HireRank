import { useState, useEffect } from 'react'
import { useLocation, useNavigate, useParams, Link } from 'react-router-dom'
import { getCandidate } from '../../services/api'
import { FiArrowLeft, FiUser, FiBriefcase, FiMail, FiPhone, FiMapPin, FiAward, FiBook, FiTool, FiTrendingUp } from 'react-icons/fi'
import ProgressBar from '../Common/ProgressBar'
import LoadingSpinner from '../Common/LoadingSpinner'
import Header from '../Layout/Header'
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
    skills,
    expected_skills,
    contact_info,
    candidate_info,
    summary,
    uploaded_at,
    resume_text,
    education,
    experience,
    awards,
    certifications
  } = result
  
  // Fallback to skills array if skills_found is not available
  // If skills_found doesn't exist but we have skills and expected_skills, calculate it
  let displaySkillsFound = skills_found
  let displaySkillsMissing = skills_missing
  
  if (!displaySkillsFound && skills && expected_skills) {
    const skillsLower = skills.map(s => s.toLowerCase())
    displaySkillsFound = expected_skills.filter(s => skillsLower.includes(s.toLowerCase()))
    displaySkillsMissing = expected_skills.filter(s => !skillsLower.includes(s.toLowerCase()))
  } else if (!displaySkillsFound) {
    displaySkillsFound = skills || []
    displaySkillsMissing = displaySkillsMissing || []
  }
  
  // Ensure they're arrays
  displaySkillsFound = displaySkillsFound || []
  displaySkillsMissing = displaySkillsMissing || []

  // Helper function to categorize skills
  const categorizeSkills = (skillsList) => {
    const categories = {
      frontend: [],
      backend: [],
      database: [],
      infrastructure: []
    }

    const categoryKeywords = {
      frontend: ['react', 'angular', 'vue', 'html', 'css', 'javascript', 'typescript', 'jquery', 'bootstrap', 'tailwind', 'sass', 'webpack', 'vite', 'next.js', 'svelte'],
      backend: ['django', 'flask', 'fastapi', 'node.js', 'express', 'spring', 'java', 'python', 'ruby', 'php', 'laravel', '.net', 'go', 'rust', 'scala', 'kotlin'],
      database: ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 'dynamodb', 'elasticsearch', 'neo4j', 'mariadb', 'firebase', 'pandas', 'numpy'],
      infrastructure: ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible', 'nginx', 'apache', 'linux', 'ci/cd', 'devops']
    }

    skillsList.forEach(skill => {
      const skillLower = skill.toLowerCase()
      let categorized = false

      for (const [category, keywords] of Object.entries(categoryKeywords)) {
        if (keywords.some(keyword => skillLower.includes(keyword) || keyword.includes(skillLower))) {
          categories[category].push(skill)
          categorized = true
          break
        }
      }

      // If not categorized, try to guess based on common patterns
      if (!categorized) {
        if (skillLower.includes('ml') || skillLower.includes('learning') || skillLower.includes('ai') || 
            skillLower.includes('tensorflow') || skillLower.includes('pytorch') || skillLower.includes('keras') ||
            skillLower.includes('scikit') || skillLower.includes('nlp')) {
          categories.backend.push(skill)
        } else if (skillLower.includes('visual') || skillLower.includes('plot') || 
                   skillLower.includes('matplotlib') || skillLower.includes('seaborn')) {
          categories.frontend.push(skill)
        } else if (skillLower.includes('jupyter') || skillLower.includes('notebook')) {
          categories.infrastructure.push(skill)
        }
      }
    })

    return categories
  }

  // Categorize skills found and missing
  const categorizedSkillsFound = categorizeSkills(displaySkillsFound)
  const categorizedSkillsMissing = categorizeSkills(displaySkillsMissing)

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
          {(contact_info || candidate_info) && (
            <div className="contact-section">
              <h3 className="section-title">Contact Information</h3>
              <div className="contact-grid">
                {((contact_info && contact_info.email) || (candidate_info && candidate_info.email)) && (
                  <div className="contact-item">
                    <FiMail className="contact-icon" />
                    <a href={`mailto:${contact_info?.email || candidate_info?.email}`} className="contact-link">
                      {contact_info?.email || candidate_info?.email}
                    </a>
                  </div>
                )}
                {((contact_info && contact_info.phone) || (candidate_info && candidate_info.phone)) && (
                  <div className="contact-item">
                    <FiPhone className="contact-icon" />
                    <a href={`tel:${contact_info?.phone || candidate_info?.phone}`} className="contact-link">
                      {contact_info?.phone || candidate_info?.phone}
                    </a>
                  </div>
                )}
                {contact_info?.location && (
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

        {/* Categorized Skills Section */}
        <div className="categorized-skills-section">
          <h2 className="section-title">Skills Analysis</h2>
          
          {/* Skills Found by Category */}
          <div className="category-skills-container">
            <h3 className="category-header">
              <svg className="category-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Skills Found ({displaySkillsFound.length})
            </h3>
            <div className="skills-categories-grid">
              {Object.entries(categorizedSkillsFound).map(([category, skillsList]) => {
                if (skillsList.length === 0) return null;
                
                return (
                  <div key={category} className="category-card category-match">
                    <h4 className="category-name">{category}</h4>
                    <div className="category-skills">
                      {skillsList.map((skill, idx) => (
                        <span key={idx} className="skill-tag skill-found">{skill}</span>
                      ))}
                    </div>
                  </div>
                );
              })}
              {Object.values(categorizedSkillsFound).every(arr => arr.length === 0) && (
                <p className="no-skills-message">No matching skills found</p>
              )}
            </div>
          </div>

          {/* Skills Missing by Category */}
          <div className="category-skills-container">
            <h3 className="category-header">
              <svg className="category-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Skills Missing ({displaySkillsMissing.length})
            </h3>
            <div className="skills-categories-grid">
              {Object.entries(categorizedSkillsMissing).map(([category, skillsList]) => {
                if (skillsList.length === 0) return null;
                
                return (
                  <div key={category} className="category-card category-missing">
                    <h4 className="category-name">{category}</h4>
                    <div className="category-skills">
                      {skillsList.map((skill, idx) => (
                        <span key={idx} className="skill-tag skill-missing">{skill}</span>
                      ))}
                    </div>
                  </div>
                );
              })}
              {Object.values(categorizedSkillsMissing).every(arr => arr.length === 0) && (
                <p className="no-skills-message">All required skills found! 🎉</p>
              )}
            </div>
          </div>
        </div>

        {/* Original Skills Grid (Hidden - kept for reference) */}
        {false && (
          <div className="skills-grid">
            {/* Skills Found */}
            <div className="skills-card skills-found-card">
              <h3 className="skills-title">
                <svg className="skills-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Skills Found ({displaySkillsFound?.length || 0})
              </h3>
              <div className="skills-list">
                {displaySkillsFound && displaySkillsFound.length > 0 ? (
                  displaySkillsFound.map((skill, index) => (
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
                Skills Missing ({displaySkillsMissing?.length || 0})
              </h3>
              <div className="skills-list">
                {displaySkillsMissing && displaySkillsMissing.length > 0 ? (
                  displaySkillsMissing.map((skill, index) => (
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
        )}

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
