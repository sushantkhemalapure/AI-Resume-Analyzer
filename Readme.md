# 🚀 ATS Resume Analyzer

AI-powered recruitment insights and candidate analysis system with Applicant Tracking System (ATS) compatibility scoring.

## 📋 Features

- **Resume Parsing**: Extract text from PDF, DOCX, and TXT files
- **Multi-language Support**: Detect and process resumes in multiple languages
- **Skill Extraction**: Identify and categorize technical and soft skills
- **ATS Scoring**: Calculate compatibility scores across multiple dimensions
- **Job Matching**: Compare resumes against job descriptions
- **Candidate Ranking**: Rank multiple candidates for a position
- **Interactive Dashboard**: Modern, gradient-based UI with real-time analytics
- **Demo Mode**: Explore features with realistic mock data

## 🏗️ Project Structure

```
AI-Resume-Analyzer/
│
├── data/                          # Data files
│   ├── skills.csv                 # Skills database
│   └── job_roles.csv              # Job role requirements
│
├── nlp/                           # NLP & Text Processing
│   ├── language_handler.py        # Multi-language support
│   ├── resume_parser.py           # Document parsing
│   └── skill_extractor.py         # Skill extraction
│
├── scoring/                       # Scoring Algorithms
│   ├── ats_score.py               # ATS compatibility scoring
│   └── similarity.py              # Job matching & ranking
│
├── api/                           # API Layer
│   ├── main.py                    # FastAPI application
│   └── routes.py                  # API routes (future)
│
├── app/                           # Frontend
│   ├── templates/
│   │   └── index.html             # Main dashboard
│   └── static/
│       ├── css/
│       │   └── style.css          # Modern styles
│       ├── js/
│       │   └── app.js             # Interactive functionality
│       └── images/
│
├── requirements.txt               # Python dependencies
├── README.md                      # Documentation
└── LICENSE                        # License file
```
