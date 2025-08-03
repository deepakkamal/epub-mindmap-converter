# 📚 EPUB to Mindmap Converter

> Transform your EPUB books into interactive, AI-powered mindmaps with ease

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Try_Now!-blue?style=for-the-badge&logo=railway)](https://web-production-df20d.up.railway.app/)
[![GitHub Stars](https://img.shields.io/github/stars/deepakkamal/epub-mindmap-converter?style=social)](https://github.com/deepakkamal/epub-mindmap-converter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

## 📋 Table of Contents

- [About](#-about)
- [Project Origin & Motivation](#-project-origin--motivation)
- [Quick Start](#-quick-start)
  - [🔑 Getting Your OpenAI API Key](#-getting-your-openai-api-key)
  - [🚀 Using the Live Demo](#-using-the-live-demo)
  - [💻 Local Development](#-local-development)
- [EPUB Processing Pipeline](#-epub-processing-pipeline)
- [Project Architecture](#-project-architecture)
- [Contributing](#-contributing)
- [Self-hosting](#-self-hosting)
- [Resources](#-resources)
- [License](#-license)
- [Documentation](#-documentation)

## 🎯 About

**EPUB to Mindmap Converter** is a powerful, AI-driven web application that transforms EPUB books into interactive mindmaps. Built with Flask and powered by OpenAI's GPT models, it provides an intuitive interface for extracting, processing, and visualizing book content in a structured, mind-map format.

### ✨ Key Features

- **🎯 Drag & Drop Interface**: Intuitive file upload with visual feedback
- **🤖 AI-Powered Processing**: Uses OpenAI GPT models for intelligent content analysis  
- **📖 Chapter Selection**: Choose specific chapters to process
- **⚡ Real-time Progress**: Live progress tracking with animations
- **📊 Multiple Export Formats**: Download as Markdown, DOCX, or PDF
- **🎨 Interactive UI**: Modern, responsive design that works on all devices
- **🔒 Secure Processing**: Files processed in isolated sessions with automatic cleanup
- **⚙️ Flexible Configuration**: Customizable AI models and processing options

## 🌟 Project Origin & Motivation

This project was born from the need to quickly understand and visualize complex information in books. Traditional reading can be time-consuming when you need to extract key concepts and relationships. By leveraging AI to create structured mindmaps, this tool helps:

- **Students** quickly grasp book concepts and create study materials
- **Researchers** extract key information and relationships from literature  
- **Professionals** create summaries and presentations from technical books
- **Educators** develop teaching materials and course outlines

The goal is to make knowledge more accessible and actionable through visual representation.

## 🚀 Quick Start

### 🔑 Getting Your OpenAI API Key

To use this application, you'll need an OpenAI API key. Here's how to get one:

1. **Create an OpenAI Account**
   - Visit [platform.openai.com](https://platform.openai.com) (not chatgpt.com)
   - Click "Sign Up" or log in if you already have an account
   - Verify your email address

2. **Access the API Dashboard**
   - Once logged in, navigate to the API section
   - Click on your profile icon in the top right
   - Select "View API keys" from the dropdown

3. **Create Your API Key**
   - Click "Create new secret key"
   - Give your key a descriptive name (e.g., "EPUB Mindmap Converter")
   - Select appropriate permissions (Full access recommended)
   - Click "Create secret key"

4. **Secure Your Key**
   - **Copy the key immediately** - you won't be able to see it again
   - Store it securely (consider using a password manager)
   - Never share it publicly or commit it to version control

5. **Add Billing Information**
   - Go to the Billing section in your OpenAI dashboard
   - Add a payment method
   - Add at least $5 credit to your account (minimum required)

6. **Monitor Usage**
   - Track your API usage in the OpenAI dashboard
   - Set usage limits to avoid unexpected charges
   - The app uses cost-effective models (GPT-4o-mini by default)

> **💡 Tip**: Start with GPT-4o-mini model for cost-effective processing. You can upgrade to GPT-4 for higher quality results if needed.

### 🚀 Using the Live Demo

1. **Visit the Application**: [https://web-production-df20d.up.railway.app/](https://web-production-df20d.up.railway.app/)
2. **Enter Your API Key**: Paste your OpenAI API key in the configuration section
3. **Upload an EPUB**: Drag and drop or select your EPUB file (up to 50MB)
4. **Select Chapters**: Choose which chapters you want to convert to mindmaps
5. **Generate Mindmaps**: Click "Generate Mindmaps" and wait for processing
6. **Download Results**: Get your mindmaps in Markdown, DOCX, or PDF format

### 💻 Local Development

```bash
# Clone the repository
git clone https://github.com/deepakkamal/epub-mindmap-converter.git
cd epub-mindmap-converter

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the application
python app.py

# Open your browser to http://localhost:5000
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Required Libraries**:
   Make sure you have the required dependencies from the parent directories:
   - `epub_to_markdown.py` from `mark_it_down_phase_2`
   - `main.py` from `mind_map_creator_phase_2`

## Usage

1. **Start the Web Server**:
   ```bash
   python app.py
   ```

2. **Open Browser**:
   Navigate to `http://localhost:5000` (or your deployed URL)

3. **Upload EPUB**:
   - Drag and drop your EPUB file onto the upload area
   - Or click "Choose File" to browse and select
   - Adjust processing settings if needed

4. **Select Chapters**:
   - Wait for EPUB processing to complete
   - Review extracted chapters
   - Select chapters you want to convert to mindmaps
   - Click "Generate Mindmaps"

5. **Download Results**:
   - Download combined results as a single markdown file
   - Or download individual chapter analyses

## Deployment

For deploying this application to cloud platforms (Heroku, Railway, Render, etc.), see the detailed [Deployment Guide](DEPLOYMENT.md).

### Quick Deploy to Heroku

1. Clone the repository
2. Set your OpenAI API key: `heroku config:set OPENAI_API_KEY=your_key`
3. Deploy: `git push heroku main`

### Environment Variables

Required for deployment:
- `OPENAI_API_KEY`: Your OpenAI API key
   - Files include mindmaps, summaries, and explanations

## Configuration

### Processing Settings

- **Minimum Chapter Length**: Filters out chapters shorter than specified character count
- **Include Back Matter**: Option to include glossary, author info, etc.

### File Limits

- Maximum file size: 100MB
- Supported format: EPUB only

## File Structure

```
web_interface/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Main web interface
├── static/               # Static assets (auto-generated)
├── uploads/              # Temporary file uploads
├── outputs/              # Processing results
└── requirements.txt      # Python dependencies
```

## API Endpoints

- `GET /` - Main interface
- `POST /upload` - File upload
- `GET /status` - Processing status
- `GET /chapters` - List processed chapters
- `POST /process-mindmaps` - Start mindmap generation
- `GET /download-combined` - Download all results
- `GET /download-chapter/<name>` - Download individual chapter

## Workflow

1. **EPUB Upload** → Extract chapters using `epub_to_markdown.py`
2. **Chapter Selection** → User selects desired chapters
3. **Mindmap Generation** → Process chapters using `main.py`
4. **Result Compilation** → Combine outputs into downloadable files
5. **Download** → Provide access to generated content

## Error Handling

- File validation (format, size)
- Processing error recovery
- Timeout handling for long operations
- Clear error messages for users
- Reset functionality to start over

## Performance

- Background processing to avoid blocking
- Progress tracking for long operations
- Efficient file handling
- Session-based state management
- Automatic cleanup of temporary files

## Troubleshooting

**Upload Issues**:
- Check file format (must be .epub)
- Verify file size (max 100MB)
- Ensure stable internet connection

**Processing Errors**:
- Check that required Python modules are available
- Verify file permissions in upload/output directories
- Review server logs for detailed error messages

**Browser Issues**:
- Enable JavaScript
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Clear browser cache if issues persist

## Development

To run in development mode:
```bash
export FLASK_ENV=development
python app.py
```

The interface will automatically reload when you make changes to the code.

## 🚀 Deployment

This application is deployed on **Railway** for easy, reliable hosting. 

### Deploy Your Own Instance

You can easily deploy your own instance of this application:

#### Option 1: Railway (Recommended)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/github_repo/deepakkamal/epub-mindmap-converter)

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Fork this repository 
4. Set environment variables:
   - `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - `SECRET_KEY` - Any random string for Flask sessions
5. Deploy automatically!

#### Other Platforms
This app is also configured for:
- **Heroku** (using `Procfile`)
- **Vercel** (using `vercel.json`)
- **Docker** (using `Dockerfile`)
- **Google Cloud Run**

See `DEPLOYMENT.md` for detailed instructions for each platform.

## Security Notes

- Files are processed in isolated session directories
- Temporary files are automatically cleaned up
- File upload validation prevents malicious uploads
- No sensitive data is stored permanently
