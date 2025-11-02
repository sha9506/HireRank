import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeResume } from '../services/api'
import { FiUpload, FiFile, FiX } from 'react-icons/fi'
import './UploadSection.css'

function UploadSection({ onAnalysisComplete, onAnalysisStart, onAnalysisEnd, onError, disabled }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [showFullDescription, setShowFullDescription] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const validateAndSetFile = (file) => {
    const validTypes = [
      'application/pdf', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
      'application/msword',
      'image/jpeg',
      'image/jpg',
      'image/png'
    ]
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!validTypes.includes(file.type)) {
      onError('Please upload a PDF, DOCX, or image file (JPG, PNG) only')
      return
    }

    if (file.size > maxSize) {
      onError('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!selectedFile) {
      onError('Please select a resume file')
      return
    }

    if (!jobTitle.trim()) {
      onError('Please enter a job title')
      return
    }

    try {
      onAnalysisStart()
      const result = await analyzeResume(
        selectedFile, 
        jobTitle, 
        jobDescription.trim() || null
      )
      onAnalysisComplete(result)
      onAnalysisEnd()
      
      // Reset form
      setSelectedFile(null)
      setJobTitle('')
      setJobDescription('')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Navigate to candidate details page
      navigate('/candidate-details', { state: { result } })
    } catch (error) {
      onAnalysisEnd()
      if (error.response?.data?.detail) {
        onError(error.response.data.detail)
      } else if (error.message) {
        onError(error.message)
      } else {
        onError('Failed to analyze resume. Please check your connection and try again.')
      }
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="upload-card">
      <h2 className="upload-title">Upload Resume</h2>

      <form onSubmit={handleSubmit} className="upload-form">
        {/* Job Title */}
        <div className="form-group">
          <label className="form-label">
            Job Title <span className="required">*</span>
          </label>
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g., Data Scientist, Software Engineer, Full Stack Developer"
            className="form-input"
            disabled={disabled}
            required
          />
          <p className="form-hint">
            💡 System will auto-detect required skills based on job title
          </p>
        </div>

        {/* File Upload */}
        <div className="form-group">
          <label className="form-label">
            Resume File <span className="required">*</span>
          </label>
          
          {!selectedFile ? (
            <div
              className={`dropzone ${dragActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => !disabled && fileInputRef.current?.click()}
            >
              <FiUpload className="dropzone-icon" />
              <p className="dropzone-text">
                <span className="highlight">Click to upload</span> or drag and drop
              </p>
              <p className="dropzone-hint">PDF, DOCX, or Image (JPG, PNG) - MAX. 10MB</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,image/jpeg,image/jpg,image/png"
                onChange={handleFileChange}
                disabled={disabled}
              />
            </div>
          ) : (
            <div className="file-preview">
              <div className="file-preview-content">
                <div className="file-info">
                  <FiFile className="file-icon" />
                  <div>
                    <p className="file-name">{selectedFile.name}</p>
                    <p className="file-size">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={removeFile}
                  className="remove-file-btn"
                  disabled={disabled}
                >
                  <FiX />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Optional Full Job Description */}
        <div className="form-group">
          <div className="optional-section-header" onClick={() => setShowFullDescription(!showFullDescription)}>
            <label className="form-label">
              Full Job Description (Optional)
            </label>
            <button type="button" className="toggle-btn">
              {showFullDescription ? '▼' : '▶'}
            </button>
          </div>
          
          {showFullDescription && (
            <>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Add full job description for more accurate matching (optional)..."
                rows={6}
                className="form-textarea"
                disabled={disabled}
              />
              <p className="char-count">{jobDescription.length} characters</p>
            </>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={disabled || !selectedFile || !jobTitle.trim()}
          className="submit-btn"
        >
          {disabled ? (
            <span className="submit-btn-content">
              <svg className="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </span>
          ) : (
            'Analyze Resume'
          )}
        </button>
      </form>
    </div>
  )
}

export default UploadSection
