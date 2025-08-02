# Project Structure for Deployment

When deploying the EPUB to Mindmap Converter, ensure your repository includes the following structure:

```
your-repository/
├── web_interface/                 # Main web application
│   ├── app.py                    # Flask application
│   ├── wsgi.py                   # WSGI entry point for deployment
│   ├── requirements.txt          # Python dependencies
│   ├── Procfile                  # Heroku process file
│   ├── Dockerfile               # Docker container configuration
│   ├── vercel.json              # Vercel deployment configuration
│   ├── app.json                 # Heroku one-click deploy configuration
│   ├── .env.example             # Environment variables template
│   ├── .gitignore              # Git ignore patterns
│   ├── README.md               # Usage instructions
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── templates/
│   │   └── index.html          # Web interface template
│   └── .github/
│       └── workflows/
│           └── deploy.yml      # GitHub Actions CI/CD
│
├── mark_it_down_phase_2/         # EPUB processing module
│   ├── epub_to_markdown.py     # Main EPUB converter
│   └── requirements.txt        # Dependencies for EPUB processing
│
└── mind_map_creator_phase_2/     # AI mindmap generation
    ├── main.py                 # CLI interface for mindmap generation
    ├── requirements.txt        # AI processing dependencies
    └── src/                   # Source modules
        └── mind_map_creator/
```

## Critical Files for Deployment

### Required in Root Web Interface Directory:
- `app.py` - Main Flask application
- `wsgi.py` - Production WSGI entry point
- `requirements.txt` - Python dependencies
- `templates/index.html` - Web interface

### Platform-Specific Files:
- `Procfile` - For Heroku deployment
- `Dockerfile` - For Docker/container deployment
- `vercel.json` - For Vercel deployment
- `app.json` - For Heroku one-click deploy

### Configuration Files:
- `.env.example` - Environment variables template
- `.gitignore` - Exclude sensitive files from Git
- `DEPLOYMENT.md` - Deployment instructions

## Environment Variables Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your actual values
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key

## Deployment Checklist

- [ ] All required files are in the repository
- [ ] Environment variables are configured
- [ ] `.env` file is NOT committed to Git
- [ ] Dependencies are listed in `requirements.txt`
- [ ] Platform-specific configuration files are present
- [ ] OpenAI API key is set in deployment environment
- [ ] File upload directories will be created automatically

## Security Notes

1. **Never commit `.env` files** - they contain sensitive API keys
2. **Use environment variables** for all configuration
3. **Set proper security headers** (handled automatically)
4. **Monitor API usage** to control costs

## Support

For deployment issues:
1. Check the logs of your deployment platform
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check that file paths are correct for your platform
