# XHS Spider - Xiaohongshu Data Collection Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> **Note**: This is a fork of the original [XHS Spider](https://github.com/original-author/Spider_XHS) project, translated and adapted for international use.

A professional data collection solution for Xiaohongshu (Little Red Book), supporting note scraping with Excel and media export capabilities.

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. Users are responsible for complying with Xiaohongshu's Terms of Service and applicable laws. The authors do not endorse or encourage any unauthorized data collection or violation of platform policies.

## Features

### Data Collection Capabilities
- ✅ User profile information
- ✅ Note details (text, images, videos)
- ✅ Search results scraping
- ✅ Comments extraction
- ✅ User posts, likes, and favorites

### Technical Features
- 🚀 High-performance architecture with automatic retry mechanism
- 🔒 Secure and stable with latest API adaptation
- 🎨 Structured data storage (JSON/Excel/Media formats)
- 🌐 Proxy support for enhanced reliability

## Requirements

- Python 3.7+
- Node.js 18+
- Valid Xiaohongshu account (for cookie authentication)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jackmeson1/Spider_XHS.git
cd Spider_XHS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

3. Configure authentication:
   - Copy `.env.example` to `.env`
   - Add your Xiaohongshu cookie (see Authentication section)

## Authentication

To obtain your cookie:
1. Log in to Xiaohongshu in your browser
2. Open Developer Tools (F12)
3. Go to Network tab → Fetch/XHR
4. Find any API request and copy the cookie value
5. Paste it in your `.env` file

## Usage

### Basic Usage
```bash
python main.py
```

### Search and Download
```bash
python main.py --query "keyword" --num 5 --save-choice all --excel-name output
```

### Save Options
- `all`: Save Excel and media files
- `excel`: Save Excel only
- `media`: Save videos and images
- `media-image`: Save images only
- `media-video`: Save videos only

### Additional Options
- `--transcode`: Convert videos to H.264 (requires ffmpeg)

## Project Structure

```
Spider_XHS/
├── main.py                 # Main entry point
├── apis/
│   ├── xhs_pc_apis.py     # PC platform APIs
│   └── xhs_creator_apis.py # Creator platform APIs
├── data/                   # Output directory
└── requirements.txt        # Python dependencies
```

## Legal Notice

- This tool is for personal use and research only
- Respect intellectual property rights
- Do not use for commercial purposes without permission
- Users assume all risks associated with using this tool

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear descriptions

## Acknowledgments

- Original project by [original author name]
- Contributors who helped improve this tool

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: If you encounter any issues or have questions, please open an issue on GitHub.
