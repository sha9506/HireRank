import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="loading-container">
      <div className="loading-content">
        {/* Spinner */}
        <div className="spinner-wrapper">
          <div className="spinner-track"></div>
          <div className="spinner-circle"></div>
        </div>

        {/* Loading Text */}
        <h3 className="loading-title">Analyzing Resume...</h3>
        <p className="loading-subtitle">This may take a few moments</p>

        {/* Progress Steps */}
        <div className="progress-steps">
          <div className="progress-step">
            <div className="step-indicator completed">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span className="step-text completed">Extracting text from resume</span>
          </div>

          <div className="progress-step">
            <div className="step-indicator active">
              <div className="step-dot"></div>
            </div>
            <span className="step-text active">Analyzing with AI models</span>
          </div>

          <div className="progress-step">
            <div className="step-indicator pending"></div>
            <span className="step-text pending">Generating insights</span>
          </div>

          <div className="progress-step">
            <div className="step-indicator pending"></div>
            <span className="step-text pending">Calculating match score</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
