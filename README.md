 🤖 AI HR Recruitment Agent

An intelligent recruitment automation system that leverages AI to streamline the entire hiring process - from job description analysis to candidate outreach.

## ✨ Features

- **🔍 AI-Powered Job Analysis**: Uses Google Gemini to extract skills, requirements, and qualifications from job descriptions
- **🎯 Smart Candidate Sourcing**: Automatically finds and ranks potential candidates based on job requirements
- **📧 Personalized Outreach**: Generates tailored recruitment emails using Ollama's local AI models
- **📊 Comprehensive Tracking**: Tracks all candidate interactions, responses, and recruitment metrics
- **📈 Advanced Analytics**: Provides detailed reports and insights into recruitment performance
- **🌐 Web Interface**: User-friendly Streamlit dashboard for easy management
- **⚡ CLI Support**: Command-line interface for automation and scripting

## 🛠️ Tech Stack

- **AI Services**: Google Gemini API + Ollama (local AI)
- **Backend**: Python with SQLite database
- **Frontend**: Streamlit web application
- **Data Processing**: Pandas, JSON
- **Visualization**: Plotly charts
- **APIs**: Mock LinkedIn API (easily replaceable with real API)

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally
- Google Gemini API key

### 2. Installation

```bash
# Clone or download the project
cd "HR automation"

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configuration

Edit your `.env` file:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
DATABASE_PATH=./data/hr_recruitment.db
```

### 4. Launch the System

#### Web Interface (Recommended)
```bash
python main.py web
```
or
```bash
streamlit run src/streamlit_app.py
```

#### Command Line Interface
```bash
# Add a new job
python main.py job add --description "Your job description here" --company "Company Name"

# Source candidates for a job
python main.py source 1 --max-candidates 20

# Run outreach campaign
python main.py outreach 1 --min-score 0.7 --preview

# Generate daily report
python main.py report daily --format json
```

## 📋 Usage Guide

### 1. Job Management

**Add a New Job:**
1. Navigate to "Job Management" in the web interface
2. Paste your job description in the text area
3. Click "Analyze & Post Job"
4. The AI will extract requirements and save the job

**Via CLI:**
```bash
python main.py job add -d "Your job description" -c "Company Name"
```

### 2. Candidate Sourcing

**Web Interface:**
1. Go to "Candidate Sourcing"
2. Select a job from the dropdown
3. Adjust sourcing parameters (max candidates, min match score)
4. Click "Start Candidate Sourcing"

**CLI:**
```bash
python main.py source 1 --max-candidates 20
```

### 3. Outreach Campaigns

**Generate Personalized Emails:**
1. Navigate to "Outreach Campaigns"
2. Select job and set campaign parameters
3. Click "Generate Outreach Campaign"
4. Review email previews
5. Send emails (simulated in demo mode)

**CLI:**
```bash
# Preview emails
python main.py outreach 1 --preview

# Send outreach campaign
python main.py outreach 1 --min-score 0.7 --max-outreach 10
```

### 4. Reports & Analytics

**Daily Reports:**
```bash
python main.py report daily
python main.py report daily --format json --date 2024-01-15
```

**Executive Summary:**
```bash
python main.py report executive
```

## 🏗️ System Architecture

```
AI HR Recruitment Agent
├── 🧠 AI Services
│   ├── Google Gemini (Job analysis, NLP tasks)
│   └── Ollama (Email generation, candidate scoring)
├── 💾 Data Layer
│   ├── SQLite Database (Candidates, Jobs, Outreach)
│   └── File Storage (Reports, Exports)
├── 🔍 Candidate Sourcing
│   ├── Mock LinkedIn API (Demo)
│   └── Candidate Ranking Algorithm
├── 📧 Outreach System
│   ├── Email Generation (AI-powered)
│   └── Campaign Management
├── 📊 Reporting
│   ├── Daily Metrics
│   ├── Executive Summaries
│   └── Data Exports
└── 🌐 Interfaces
    ├── Streamlit Web App
    └── Command Line Interface
```

## 📊 Database Schema

### Jobs Table
- `id`, `title`, `company`, `description`
- `required_skills` (JSON), `experience_level`, `location`
- `posted_date`, `status`

### Candidates Table
- `id`, `name`, `email`, `linkedin_url`
- `skills` (JSON), `experience_years`, `location`, `summary`
- `match_score`, `job_id`, `sourced_date`
- `last_contacted`, `response_status`, `notes`

### Outreach Log
- `id`, `candidate_id`, `job_id`, `outreach_date`
- `message_content`, `platform`, `status`, `response_content`

### Daily Reports
- `id`, `report_date`, metrics, `report_data` (JSON)

## 🔧 Customization

### Adding Real LinkedIn API

Replace the `MockLinkedInAPI` class in `src/hr_agent.py`:

```python
class LinkedInAPI:
    def __init__(self, client_id, client_secret):
        # Initialize LinkedIn API client
        pass
    
    def search_candidates(self, skills, location, experience_min):
        # Implement real LinkedIn search
        pass
```

### Email Integration

Add SMTP configuration to send real emails:

```python
import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, content):
    # Implement actual email sending
    pass
```

### Advanced AI Models

Customize AI models in the configuration:

```env
OLLAMA_MODEL=llama3.1:70b  # Use larger model for better results
```

## 📈 Key Metrics Tracked

- **Daily Metrics**: Candidates sourced, shortlisted, contacted, responses
- **Match Scores**: AI-calculated compatibility between candidates and jobs
- **Response Rates**: Track email campaign effectiveness
- **Pipeline Status**: Overview of all active recruitment processes
- **Performance Trends**: Weekly and monthly recruitment trends

## 🔒 Privacy & Security

- **Data Privacy**: All candidate data stored locally in SQLite
- **API Security**: API keys stored in environment variables
- **Local AI**: Ollama runs locally for sensitive data processing
- **Configurable**: Easy to deploy on-premises for maximum data control

## 🧪 Testing

The system includes sample data and mock APIs for testing:

1. **Sample Job Descriptions**: Located in `templates/sample_job_descriptions.json`
2. **Mock Candidates**: Built into the system for demonstration
3. **Test Commands**: Use CLI to test individual components

Example test workflow:
```bash
# Test the full pipeline
python main.py job add -d "Python developer with Django experience" -c "TestCorp"
python main.py source 1
python main.py outreach 1 --preview
python main.py report daily
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - feel free to use and modify for your recruitment needs.

## 🆘 Troubleshooting

### Common Issues

**Ollama Connection Failed:**
- Ensure Ollama is running: `ollama serve`
- Check the model is available: `ollama list`
- Pull required model: `ollama pull llama3.1:8b`

**Gemini API Errors:**
- Verify API key is correct
- Check API quota and billing
- Ensure API is enabled in Google Cloud Console

**Database Issues:**
- Check write permissions for the data directory
- Verify SQLite is properly installed

### Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the error logs in the terminal
3. Ensure all dependencies are installed correctly

---

**Ready to revolutionize your recruitment process? 🚀**

Start with the web interface: `python main.py web`
