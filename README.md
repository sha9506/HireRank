# HireRank
# HireRank - AI-Powered Resume Ranking Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![React](https://img.shields.io/badge/react-18.2-61dafb)]()

HireRank is a full-stack AI-powered resume ranking and talent screening platform that helps recruiters efficiently analyze and rank candidate resumes based on job requirements using advanced NLP models.

## 🎯 Features

- **AI-Powered Analysis**: Uses HuggingFace Transformers (BERT, SentenceTransformer) for semantic similarity analysis
- **Resume Parsing**: Supports PDF and DOCX format resume uploads
- **Smart Ranking**: Calculates match scores (0-100) based on job description relevance
- **Skill Extraction**: Automatically identifies and extracts key technical and soft skills
- **AI Summaries**: Generates human-readable explanations for candidate fit
- **Dark Mode**: Beautiful light/dark theme toggle
- **Responsive Design**: Modern UI built with React and TailwindCSS
- **Scalable Architecture**: Containerized with Docker and deployable on Kubernetes

## 🏗️ Architecture

```
Frontend (React + Vite + TailwindCSS)
          ↓
Backend (FastAPI + Python)
          ↓
    ┌─────┴─────┐
    ↓           ↓
MongoDB    NLP Models
           (HuggingFace)
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Icons**: React Icons

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Database**: MongoDB (Motor async driver)
- **Resume Parsing**: pdfminer.six, docx2txt
- **NLP/ML**: 
  - sentence-transformers (all-MiniLM-L6-v2)
  - transformers (BART for summarization)
  - PyTorch
- **ASGI Server**: Uvicorn

### DevOps
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins
- **Proxy**: Nginx

## 📁 Project Structure

```
HireRank/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── resume_processor.py # Resume text extraction
│   │   ├── nlp_analyzer.py     # NLP analysis & similarity
│   │   └── database.py         # MongoDB operations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── UploadSection.jsx
│   │   │   ├── ResultsSection.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── context/
│   │   │   └── ThemeContext.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── deploy/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── mongo-deployment.yaml
│   ├── services.yaml
│   └── ingress.yaml
├── docker-compose.yml
├── Jenkinsfile
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- MongoDB (or use Docker)
- Kubernetes cluster (Minikube/Docker Desktop/AWS EKS) for K8s deployment

### Option 1: Docker Compose (Recommended for Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HireRank.git
   cd HireRank
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB** (if not using Docker)
   ```bash
   mongod --dbpath /path/to/data
   ```

6. **Run the backend**
   ```bash
   python main.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

### Option 3: Kubernetes Deployment

1. **Build Docker images**
   ```bash
   docker build -t hirerank-backend:latest ./backend
   docker build -t hirerank-frontend:latest ./frontend
   ```

2. **Apply Kubernetes manifests**
   ```bash
   kubectl apply -f deploy/mongo-deployment.yaml
   kubectl apply -f deploy/backend-deployment.yaml
   kubectl apply -f deploy/frontend-deployment.yaml
   kubectl apply -f deploy/services.yaml
   kubectl apply -f deploy/ingress.yaml
   ```

3. **Check deployment status**
   ```bash
   kubectl get pods
   kubectl get services
   ```

4. **Access the application**
   ```bash
   kubectl port-forward service/frontend 3000:80
   ```

## 📚 API Documentation

### Main Endpoints

#### POST /rank_resume
Analyze and rank a resume against a job description.

**Request:**
- `resume`: File (PDF/DOCX)
- `job_description`: Text
- `job_id`: String (optional)

**Response:**
```json
{
  "match_score": 85.5,
  "skills_extracted": ["Python", "React", "Docker"],
  "summary": "Excellent match: Candidate has strong technical skills...",
  "candidate_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "education": "B.Tech Computer Science",
    "experience_years": "5 years"
  },
  "analysis_id": "507f1f77bcf86cd799439011"
}
```

#### GET /health
Health check endpoint.

#### GET /analyses/{job_id}
Get all analyses for a specific job.

#### GET /top_candidates/{job_id}
Get top-ranked candidates for a job.

Full API documentation available at: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=hirerank
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📊 Features in Detail

### Resume Processing
- Extracts text from PDF and DOCX files
- Parses candidate information (name, email, phone, education)
- Estimates years of experience

### NLP Analysis
- **Semantic Similarity**: Uses sentence-transformers for deep semantic understanding
- **Skill Extraction**: Pattern matching across 60+ technical and soft skills
- **AI Summarization**: BART model generates human-readable explanations

### Frontend Features
- Drag-and-drop file upload
- Real-time analysis progress
- Beautiful dark/light theme
- Responsive design for all devices
- Detailed results with visualizations

## 🚀 Deployment

### AWS EKS
```bash
# Create EKS cluster
eksctl create cluster --name hirerank-cluster --region us-east-1

# Deploy application
kubectl apply -f deploy/
```

### Google Cloud Platform (GKE)
```bash
# Create GKE cluster
gcloud container clusters create hirerank-cluster --zone us-central1-a

# Deploy application
kubectl apply -f deploy/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- HuggingFace for the amazing Transformers library
- FastAPI for the modern Python web framework
- React team for the excellent frontend library
- The open-source community

## 📧 Contact

Project Link: [https://github.com/sha9506/HireRank](https://github.com/sha9506/HireRank)

## 🗺️ Roadmap

- [ ] JWT authentication for recruiters
- [ ] Role-based access control (HR, Admin)
- [ ] Email notifications for top candidates
- [ ] Bulk resume processing
- [ ] Resume comparison feature
- [ ] Advanced analytics dashboard
- [ ] Export reports (PDF, Excel)
- [ ] Integration with ATS systems
- [ ] Multi-language support
- [ ] Resume feedback system

---

**Built with ❤️ using React, FastAPI, and AI**
