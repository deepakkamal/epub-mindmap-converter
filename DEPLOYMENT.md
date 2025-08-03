# EPUB to Mindmap Converter - Deployment Guide

This guide covers deploying the EPUB to Mindmap Converter web application to various cloud platforms.

## Prerequisites

1. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Git repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Environment Variables

The application uses the following environment variables:

### Required
- `OPENAI_API_KEY`: Your OpenAI API key for AI model access

### Optional
- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `FLASK_DEBUG`: Set to `false` for production (default: `false`)
- `FLASK_HOST`: Host to bind to (default: `0.0.0.0`)
- `MAX_FILE_SIZE_MB`: Maximum upload file size in MB (default: `100`)
- `PORT`: Port to run on (auto-set by most platforms)

**Note**: This app uses memory-only processing - no persistent file storage directories are needed.

## Deployment Platforms

### 1. Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_api_key_here
   heroku config:set SECRET_KEY=your_secret_key_here
   heroku config:set FLASK_DEBUG=false
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Open your app**:
   ```bash
   heroku open
   ```

### 2. Railway

1. **Connect your GitHub repository** at [railway.app](https://railway.app)

2. **Add environment variables** in the Railway dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Your secret key
   - `FLASK_DEBUG`: `false`

3. **Deploy**: Railway will automatically deploy from your GitHub repository

### 3. Render

1. **Connect your GitHub repository** at [render.com](https://render.com)

2. **Create a new Web Service**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python wsgi.py`

3. **Add environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Your secret key
   - `FLASK_DEBUG`: `false`

### 4. Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Create `vercel.json`** (already included):
   ```json
   {
     "functions": {
       "wsgi.py": {
         "runtime": "python3.9"
       }
     },
     "routes": [
       {
         "src": "/(.*)",
         "dest": "wsgi.py"
       }
     ]
   }
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Set environment variables** via Vercel dashboard

### 5. Google Cloud Run

1. **Create `Dockerfile`** (already included)

2. **Build and deploy**:
   ```bash
   gcloud run deploy epub-mindmap --source .
   ```

3. **Set environment variables** via Google Cloud Console

## File Structure for Deployment

When deploying, ensure your repository includes:

```
your-repo/
├── web_interface/
│   ├── app.py                 # Main Flask app
│   ├── wsgi.py               # WSGI entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Procfile             # Heroku process file
│   ├── Dockerfile           # Docker configuration
│   ├── vercel.json          # Vercel configuration
│   ├── .env.example         # Environment variables template
│   ├── .gitignore          # Git ignore file
│   └── templates/
│       └── index.html       # Web interface
├── mark_it_down_phase_2/
│   └── epub_to_markdown.py  # EPUB processing
└── mind_map_creator_phase_2/
    ├── main.py              # Mindmap generation
    └── requirements.txt     # AI processing dependencies
```

## Security Notes

1. **Never commit your `.env` file** - it contains sensitive API keys
2. **Use strong secret keys** for production deployments
3. **Set `FLASK_DEBUG=false`** in production
4. **Monitor your OpenAI API usage** to avoid unexpected charges

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all custom modules are in the correct paths
2. **File Upload Issues**: Check file size limits and disk space
3. **API Key Errors**: Verify your OpenAI API key is correctly set
4. **Timeout Issues**: Large files may take time to process

### Logs

Check application logs for debugging:
- **Heroku**: `heroku logs --tail`
- **Railway**: View logs in Railway dashboard
- **Render**: View logs in Render dashboard

## Local Development

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your API keys

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**:
   ```bash
   python app.py
   ```

5. **Open**: http://localhost:5000

## Support

For issues related to:
- **EPUB processing**: Check `mark_it_down_phase_2/` logs
- **Mindmap generation**: Check `mind_map_creator_phase_2/` logs
- **Web interface**: Check Flask application logs
