# AI HR Recruitment Agent - Project Structure

```
HR automation/
├── 📁 src/                          # Source code directory
│   ├── 📄 __init__.py               # Package initialization
│   ├── 📄 database.py               # Database models and operations
│   ├── 📄 hr_agent.py               # Main HR agent class with AI integration
│   ├── 📄 reporting.py              # Report generation and analytics
│   └── 📄 streamlit_app.py          # Web interface (Streamlit)
│
├── 📁 data/                         # Database and data files
│   └── 📄 hr_recruitment.db         # SQLite database (gitignored)
│
├── 📁 templates/                    # Templates and examples
│   └── 📄 sample_job_descriptions.json  # Sample job descriptions for testing
│
├── 📄 main.py                       # Main CLI application
├── 📄 demo.py                       # Interactive demo script
├── 📄 quickstart.py                 # Quick setup script
├── 📄 setup.py                      # Installation and setup script
├── 📄 test_installation.py          # Installation verification script
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 .env                          # Environment variables (gitignored)
├── 📄 .gitignore                    # Git ignore patterns
├── 📄 README.md                     # Comprehensive documentation
└── 📄 PROJECT_STRUCTURE.md          # This file
```

## 📊 Component Overview

### 🧠 Core AI Components
- **Google Gemini**: Job description analysis and NLP tasks
- **Ollama**: Local AI for email generation and candidate scoring
- **Custom Algorithms**: Fallback matching and scoring systems

### 💾 Database Schema
- **Jobs**: Job postings with extracted requirements
- **Candidates**: Sourced candidates with match scores
- **Outreach Log**: Email campaigns and interactions
- **Daily Reports**: Analytics and metrics

### 🌐 Interfaces
- **Web Interface**: Streamlit dashboard at http://localhost:8501
- **CLI Interface**: Command-line tool for automation
- **API Integration**: Mock LinkedIn API (replaceable with real APIs)

### 📊 Features
- ✅ AI-powered job description analysis
- ✅ Intelligent candidate sourcing and ranking
- ✅ Personalized recruitment email generation
- ✅ Comprehensive tracking and analytics
- ✅ Interactive dashboard with charts
- ✅ Daily reporting and executive summaries
- ✅ Data export capabilities (CSV, JSON)

## 🚀 Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Setup environment: Copy `.env.example` to `.env` and add API keys
3. Test installation: `python test_installation.py`
4. Launch web interface: `python main.py web`
5. Or use CLI: `python main.py --help`

## 👥 Collaboration
This project is set up for collaborative development with proper documentation, modular architecture, and version control.
