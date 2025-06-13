import os
from .error_handler import validate_cookies

try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback for dotenv
    def load_dotenv():
        """Simple .env file parser"""
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value

try:
    from loguru import logger
except ImportError:
    # Fallback logger
    class FallbackLogger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    logger = FallbackLogger()

def load_env():
    load_dotenv()
    cookies_str = os.getenv('COOKIES') or os.getenv('XHS_COOKIE')
    
    if not cookies_str:
        logger.error("No cookies found in environment variables. Please set COOKIES or XHS_COOKIE.")
        return None
    
    if not validate_cookies(cookies_str):
        logger.error("Invalid cookies format. Please check your cookie string.")
        return None
    
    logger.info("Cookies loaded and validated successfully")
    return cookies_str

def init():
    media_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datas/media_datas'))
    excel_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datas/excel_datas'))
    for base_path in [media_base_path, excel_base_path]:
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            logger.info(f'Created directory {base_path}')
    cookies_str = load_env()
    base_path = {
        'media': media_base_path,
        'excel': excel_base_path,
    }
    return cookies_str, base_path
