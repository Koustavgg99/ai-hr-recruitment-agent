# HR Automation System

A comprehensive HR automation system that streamlines the candidate recruitment process by automatically shortlisting candidates from LinkedIn connections, generating professional documents, and sending personalized emails.

## 🌟 Features

### Core Functionality
- **Candidate Shortlisting**: Automatically matches candidates from your LinkedIn connections against job descriptions
- **LinkedIn Data Extraction**: Enhances candidate profiles using web scraping and Google search (no API required)
- **Document Generation**: Creates professional Word documents with candidate information
- **Interactive Selection**: User-friendly interface for selecting candidates from shortlists
- **Email Integration**: Sends personalized emails to selected candidates for telephonic interviews
- **Complete Workflow**: Orchestrates all components in a seamless automated process

### Key Components
1. **candidate_shortlisting.py** - Processes connections.csv and matches candidates against job descriptions
2. **linkedin_scraper.py** - Extracts additional profile data via web scraping and Google search
3. **word_generator.py** - Creates formatted Word documents and handles candidate selection
4. **email_integration.py** - Manages email communications with selected candidates
5. **hr_automation_main.py** - Main workflow orchestrator that ties everything together


## 📋 Detailed Component Guide

### Candidate Shortlisting System
- **Input**: connections.csv, job descriptions
- **Processing**: Skill matching, title similarity, scoring algorithm
- **Output**: shortlists.json with ranked candidates

**Key Features:**
- Intelligent skill extraction from job descriptions
- Position title matching
- Configurable matching thresholds
- Detailed scoring system

### LinkedIn Profile Enhancement
- **Method**: Web scraping + Google search (no API required)
- **Data Extracted**: Enhanced position info, skills, location
- **Safety**: Built-in delays, error handling, respectful scraping

**Features:**
- Fallback mechanisms for failed extractions
- Rate limiting to avoid blocking
- Multiple data sources for reliability

### Document Generation
- **Formats**: Word (.docx) and Text (.txt) fallback
- **Content**: Professional candidate summaries
- **Organization**: Job-wise grouping, detailed tables

**Generated Documents:**
- Complete shortlists document
- Selected candidates document per job
- Interactive candidate selection interface

### Email System Integration
- **Templates**: Uses existing email system
- **Personalization**: Dynamic content based on candidate data
- **Features**: Preview mode, batch processing, delivery tracking

**Email Features:**
- Personalized subject lines and content
- Professional recruitment templates
- Delivery success/failure tracking
- Email logs for audit purposes

## ⚙️ System Configuration

### Matching Algorithm
The system uses a sophisticated matching algorithm:
- **Required Skills**: 1.0 weight
- **Preferred Skills**: 0.5 weight
- **Title Similarity**: 0.2 bonus
- **Threshold**: 0.3 minimum match score

### LinkedIn Enhancement
- **Rate Limiting**: 1-3 second delays between requests
- **Fallback Strategy**: Multiple extraction methods
- **Error Handling**: Graceful degradation on failures

### Document Generation
- **Word Format**: Professional tables and formatting
- **Text Fallback**: Available when python-docx not installed
- **Customizable**: Easy template modification


### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export PYTHONPATH="$PYTHONPATH:."
python -m logging hr_automation_main.py
```

## 📈 Performance Considerations

### Processing Time
- **Basic Shortlisting**: ~30 seconds for 100 candidates
- **LinkedIn Enhancement**: ~2-5 minutes per candidate (due to rate limiting)
- **Document Generation**: ~10 seconds
- **Email Sending**: ~2 seconds per email (with delays)

### Optimization Tips
- Use auto-mode for faster processing
- Skip LinkedIn enhancement for quick results
- Process in batches for large datasets


## 🔮 Future Enhancements

Potential improvements for future versions:
- Machine learning-based candidate scoring
- Integration with ATS systems
- Advanced LinkedIn data extraction
- Analytics dashboard



**Note**: This system is designed for legitimate HR and recruitment purposes. Please use responsibly and in compliance with applicable laws and LinkedIn's terms of service.
