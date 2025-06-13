# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Xiaohongshu (Little Red Book) data collection toolkit that scrapes content from the platform. The spider supports collecting user profiles, note content, comments, search results, and media files with structured Excel export.

## Architecture

The codebase follows a modular architecture:

- **`main.py`**: Main entry point with `Data_Spider` class containing core crawling logic
- **`cli.py`**: Alternative Typer-based CLI interface 
- **`apis/`**: API layer with PC web endpoints split into functional modules (search, detail, comments, feed)
- **`xhs_utils/`**: Utility modules for common operations, data processing, and cookie management
- **`static/`**: JavaScript files for signature generation and request signing

## Key Components

### Data Spider (`main.py`)
- `Data_Spider` class orchestrates all crawling operations
- Methods: `spider_note()`, `spider_some_note()`, `spider_user_all_note()`, `spider_some_search_note()`
- Handles rate limiting, retries, and progress tracking with tqdm

### API Layer (`apis/`)
- `XHS_Apis` inherits from multiple API classes (FeedAPI, SearchAPI, DetailAPI, CommentAPI)
- Base URL: `https://edith.xiaohongshu.com`
- Uses cookie-based authentication with XHS_COOKIE/COOKIES environment variables

### Data Processing (`xhs_utils/`)
- `common_util.py`: Environment setup, cookie loading, directory initialization
- `data_util.py`: Note processing, media downloads, Excel exports
- Output directories: `datas/media_datas/`, `datas/excel_datas/`

## Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run main spider with examples
python main.py

# CLI usage
python main.py --query "search term" --num 10 --save-choice all --excel-name results
python cli.py crawl --cookie "cookie_string" --note-id "note_id"
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov
```

### Authentication
Set cookie in `.env` file:
```
COOKIES="your_cookie_value"
# or
XHS_COOKIE="your_cookie_value"
```

## Save Options
- `all`: Excel + all media files
- `excel`: Structured data only  
- `media`: Images and videos
- `media-image`: Images only
- `media-video`: Videos only
- `image-flat`: Images in flat structure
- `video-flat`: Videos in flat structure

## Important Implementation Notes

- Cookie authentication is required - extract `web_session` cookie from browser
- Rate limiting is built-in to avoid account restrictions
- Failed downloads are logged to `failed.txt` and can be retried with `--retry-failed`
- Media transcoding support with `--transcode` flag
- Geographic search filters supported with lat/lng coordinates
- Both URL-based and search-based content discovery

## Bug Fixes Applied

### Enhanced Error Handling
- **New error classes**: `XHSAuthError`, `XHSRateLimitError`, `XHSNotFoundError`, `XHSAPIError`
- **HTTP status code validation**: Proper handling of 401, 403, 404, 461, 5xx errors
- **Response structure validation**: Checks for valid JSON and required fields
- **Cookie validation**: Validates presence of required fields (`a1`, `web_session`)

### Improved Request Patterns
- **Retry logic with exponential backoff**: `@retry_with_backoff` decorator with configurable parameters
- **Smart rate limiting**: `smart_delay()` function adds intelligent delays between requests
- **Request logging**: Debug logging for all API calls with headers and data
- **Enhanced URL parsing**: Safer query parameter parsing with validation

### Key Files Modified
- `xhs_utils/error_handler.py` - New comprehensive error handling
- `xhs_utils/retry_util.py` - Retry logic with exponential backoff
- `xhs_utils/common_util.py` - Cookie validation
- `apis/pc/search.py` - Enhanced error handling for search APIs
- `apis/pc/detail.py` - Enhanced error handling for detail APIs
- `main.py` - Updated spider class with retry decorators

### Testing
Run `python3 test_fixes.py` to validate the bug fixes work correctly.