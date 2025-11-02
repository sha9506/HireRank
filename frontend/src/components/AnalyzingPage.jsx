import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from './LoadingSpinner'
import './AnalyzingPage.css'

function AnalyzingPage() {
  const navigate = useNavigate()

  useEffect(() => {
    // If someone directly navigates to this page, redirect to home
    const timer = setTimeout(() => {
      navigate('/')
    }, 3000)

    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <div className="analyzing-page">
      <div className="analyzing-content">
        <div className="analyzing-animation">
          <LoadingSpinner />
        </div>
        <h1 className="analyzing-title">Analyzing Resume...</h1>
        <p className="analyzing-subtitle">
          Our AI is processing the resume and matching it with job requirements
        </p>
        <div className="analyzing-steps">
          <div className="step">
            <div className="step-icon">✓</div>
            <span>Extracting text</span>
          </div>
          <div className="step">
            <div className="step-icon">✓</div>
            <span>Identifying skills</span>
          </div>
          <div className="step active">
            <div className="step-icon">⟳</div>
            <span>Matching with job</span>
          </div>
          <div className="step">
            <div className="step-icon">○</div>
            <span>Generating insights</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyzingPage
