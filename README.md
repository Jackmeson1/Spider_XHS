# XHS Spider - Xiaohongshu Data Collection Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Jackmeson1/Spider_XHS/pulls)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Jackmeson1/Spider_XHS/graphs/commit-activity)

> **Note**: This is a fork of the original [XHS Spider](https://github.com/cv-cat/Spider_XHS) project, enhanced with new features and international documentation.

A powerful and ethical data collection toolkit for Xiaohongshu (Little Red Book/小红书), featuring robust scraping capabilities with structured data export in multiple formats.

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#contributing">Contributing</a>
</p>

## ⚠️ Disclaimer

This tool is designed for **educational and research purposes only**. Users must:
- Comply with Xiaohongshu's Terms of Service
- Respect intellectual property rights
- Follow applicable local laws and regulations
- Use responsibly with rate limiting to avoid account restrictions

The authors assume no liability for misuse or any violations of platform policies.

## ✨ Features

### Core Capabilities
- 📊 **Comprehensive Data Collection**
  - User profiles and statistics
  - Note content (text, images, videos)
  - Comments and engagement metrics
  - Search results with filters
  - User collections and liked content

### Technical Excellence
- 🚀 **High Performance**
  - Asynchronous request handling
  - Intelligent retry mechanism
  - Built-in rate limiting
  - Concurrent download support

- 🔒 **Security & Stability**
  - Latest API compatibility (2024)
  - Cookie-based authentication
  - Proxy rotation support
  - Error handling and logging

- 💾 **Flexible Export Options**
  - Excel files with structured data
  - JSON for programmatic access
  - Media files (images/videos)
  - Custom output formatting

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Jackmeson1/Spider_XHS.git
cd Spider_XHS

# Install dependencies
pip install -r requirements.txt
npm install

# Run with basic configuration
python main.py --help
```

## 📋 Requirements

- **Python** 3.7 or higher
- **Node.js** 18.0 or higher
- **jsdom** (installed via `npm install`) for DOM emulation
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: Varies based on media download requirements

### Optional Requirements
- **FFmpeg**: For video transcoding functionality
- **Proxy Server**: For enhanced anonymity and rate limit bypass

## 🔧 Installation

### 1. System Dependencies

#### Windows
```powershell
# Install Python (if not already installed)
winget install Python.Python.3.11

# Install Node.js
winget install OpenJS.NodeJS.LTS
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11
brew install node@18
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm
```

### 2. Project Setup

```bash
# Clone the repository
git clone https://github.com/Jackmeson1/Spider_XHS.git
cd Spider_XHS

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 3. Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env file with your settings
# Required: XHS_COOKIE
# Optional: PROXY_URL, OUTPUT_DIR, etc.
```

## 🔐 Authentication

### Obtaining Your Cookie

1. **Login to Xiaohongshu**
   - Open [xiaohongshu.com](https://www.xiaohongshu.com) in Chrome/Firefox
   - Log in to your account

2. **Extract Cookie**
   - Press `F12` to open Developer Tools
   - Navigate to `Application` tab → `Cookies`
   - Copy the value of `web_session` cookie

3. **Configure Authentication**
   ```bash
   # Add to .env file
   XHS_COOKIE="your_cookie_value_here"
   ```

⚠️ **Security Note**: Never share your cookie publicly or commit it to version control.

## 📖 Usage

### Command Line Interface

```bash
# Show help
python cli.py --help

# Crawl a specific note
python cli.py crawl --note-id "64f5e8d9000000001e03c5b5"
python cli.py crawl --note-url "https://www.xiaohongshu.com/explore/64f5e8d9000000001e03c5b5"

# Specify an output directory and Excel file
python cli.py crawl --note-id "64f5e8d9000000001e03c5b5" \
  --output-dir ./out --save-choice excel --excel-name note_data

# Search and download
python cli.py search --query "travel tips" --count 20 --save-media

# Crawl user profile
python cli.py crawl-user --user-id "5f3b4c920000000001005d8b" --include-liked
```

### Python API

```python
from xhs_spider import XHSClient

# Initialize client
client = XHSClient(cookie="your_cookie_here")

# Search notes
results = client.search("keyword", count=10)

# Get note details
note = client.get_note("note_id")

# Download media
client.download_media(note, output_dir="./downloads")
```

### Advanced Options

```bash
# Full command with all options
python main.py \
  --query "makeup tutorial" \
  --num 50 \
  --save-choice all \
  --excel-name "makeup_data" \
  --transcode \
  --proxy "http://proxy.example.com:8080" \
  --rate-limit 2 \
  --retry 3
```

`--rate-limit` sets the minimum number of seconds to wait between HTTP requests.

### Save Options Explained

| Option | Description | Output |
|--------|-------------|--------|
| `all` | Complete data package | Excel + All media files |
| `excel` | Structured data only | Excel file |
| `media` | Media files only | Images + Videos |
| `media-image` | Images only | JPG/PNG files |
| `media-video` | Videos only | MP4 files |

## 📁 Project Structure

```
Spider_XHS/
├── main.py                 # Main entry point
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── .env.example           # Configuration template
├── LICENSE                # MIT License
├── README.md              # This file
├── apis/                  # API modules
│   ├── __init__.py
│   ├── auth.py           # Authentication handling
│   ├── xhs_pc_apis.py    # PC web APIs
│   ├── xhs_creator_apis.py # Creator platform APIs
│   ├── search.py         # Search functionality
│   ├── note.py           # Note operations
│   ├── user.py           # User operations
│   └── utils.py          # Utility functions
├── models/               # Data models
│   ├── __init__.py
│   ├── note.py
│   └── user.py
├── exporters/            # Export handlers
│   ├── __init__.py
│   ├── excel_exporter.py
│   ├── json_exporter.py
│   └── media_handler.py
├── tests/                # Test suite
│   ├── test_apis.py
│   └── test_exporters.py
└── data/                 # Output directory (git-ignored)
    ├── excel/
    ├── media/
    └── logs/
```

## 🔌 API Reference

### Core Classes

#### XHSClient
Main client for interacting with Xiaohongshu.

```python
client = XHSClient(
    cookie: str,           # Required: Authentication cookie
    proxy: str = None,     # Optional: Proxy URL
    timeout: int = 30,     # Request timeout in seconds
    max_retries: int = 3   # Maximum retry attempts
)
```

#### Methods

- `search(query, count, sort_type)` - Search for notes
- `get_note(note_id)` - Get note details
- `get_user(user_id)` - Get user profile
- `get_user_notes(user_id, count)` - Get user's notes
- `download_media(note, output_dir)` - Download media files

### Error Handling

The client includes comprehensive error handling:

```python
try:
    note = client.get_note("invalid_id")
except XHSAuthError:
    print("Authentication failed - check your cookie")
except XHSRateLimitError:
    print("Rate limited - please wait before retrying")
except XHSNotFoundError:
    print("Note not found")
```

## 🐛 Troubleshooting

### Common Issues

1. **Cookie Expired**
   - Solution: Obtain a fresh cookie from the browser
   
2. **Rate Limiting (Error 461)**
   - Solution: Reduce request frequency, use proxy rotation
   
3. **Media Download Fails**
   - Solution: Check network connectivity, verify media URLs

4. **Excel Export Error**
   - Solution: Ensure `openpyxl` is installed, check write permissions

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set in .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 .
black .
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Performance Metrics

| Operation | Average Time | Rate Limit |
|-----------|--------------|------------|
| Note fetch | ~500ms | 2 req/sec |
| Search | ~800ms | 1 req/sec |
| Media download | Varies | 5 concurrent |
| Excel export | ~100ms/note | N/A |

## 🔮 Roadmap

- [ ] GraphQL API support
- [ ] Batch user operations
- [ ] Live streaming data collection
- [ ] Machine learning integration for content analysis
- [ ] Web UI dashboard
- [ ] Docker containerization
- [ ] Scheduled crawling with cron support

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original [Spider_XHS](https://github.com/cv-cat/Spider_XHS) project
- [Xiaohongshu](https://www.xiaohongshu.com) for providing the platform
- All contributors who have helped improve this tool
- The open-source community for invaluable resources

## 📮 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/Jackmeson1/Spider_XHS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jackmeson1/Spider_XHS/discussions)
- **Email**: your-email@example.com

---

<p align="center">
  Made with ❤️ by the XHS Spider community
  <br>
  Star ⭐ this repository if you find it helpful!
</p>
