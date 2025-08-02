# EPUB to Mindmap Web Interface

A beautiful, user-friendly web interface for converting EPUB files into interactive mindmaps.

## 🚀 Live Demo

**Try it now!** The application is live and ready to use:

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Try_Now!-blue?style=for-the-badge&logo=railway)](https://web-production-df20d.up.railway.app/)

👆 **Click the button above to use the live application!**

🔗 **Direct link:** https://web-production-df20d.up.railway.app/

## Features

- **Drag & Drop Upload**: Easy file upload with visual feedback
- **Real-time Processing**: Live progress tracking with animations
- **Chapter Selection**: Choose which chapters to process with checkboxes
- **Batch Processing**: Generate mindmaps for multiple chapters simultaneously
- **Download Management**: Get combined results or individual chapter analyses
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Graceful error handling with clear messages

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
