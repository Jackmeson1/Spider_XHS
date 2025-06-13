"""Advanced configuration management for XHS Spider optimizations"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SearchConfig:
    """Advanced search configuration"""
    keywords: List[str]
    hashtags: List[str] = None
    users: List[str] = None
    min_likes: int = 0
    min_comments: int = 0
    max_age_days: int = 365
    content_types: List[str] = None  # ['image', 'video', 'mixed']
    categories: List[str] = None
    exclude_keywords: List[str] = None
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.users is None:
            self.users = []
        if self.content_types is None:
            self.content_types = ['image', 'video', 'mixed']
        if self.categories is None:
            self.categories = []
        if self.exclude_keywords is None:
            self.exclude_keywords = []


@dataclass
class DownloadConfig:
    """Media download configuration"""
    max_concurrent_downloads: int = 3
    timeout_seconds: int = 30
    retry_attempts: int = 3
    min_image_resolution: tuple = (500, 500)
    max_file_size_mb: int = 100
    allowed_formats: List[str] = None
    quality_threshold: float = 0.7
    auto_resize: bool = False
    target_resolution: tuple = (1080, 1080)
    
    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = ['jpg', 'jpeg', 'png', 'mp4', 'webp']


@dataclass
class FilterConfig:
    """Content filtering configuration"""
    enable_duplicate_detection: bool = True
    similarity_threshold: float = 0.85
    enable_quality_filter: bool = True
    enable_spam_detection: bool = True
    min_content_length: int = 10
    language_filter: List[str] = None
    quality_threshold: float = 0.5
    
    def __post_init__(self):
        if self.language_filter is None:
            self.language_filter = ['zh', 'en']


@dataclass
class ExportConfig:
    """Export and output configuration"""
    output_format: str = 'excel'  # excel, json, csv, database
    include_metadata: bool = True
    create_html_gallery: bool = False
    generate_thumbnails: bool = True
    organize_by_user: bool = True
    organize_by_date: bool = False
    export_comments: bool = False
    export_analytics: bool = True


@dataclass
class CrawlerConfig:
    """Main crawler configuration"""
    search: SearchConfig
    download: DownloadConfig
    filters: FilterConfig
    export: ExportConfig
    rate_limit_per_minute: int = 30
    respect_robots_txt: bool = True
    user_agent_rotation: bool = True
    proxy_rotation: bool = False
    proxy_list: List[str] = None
    
    def __post_init__(self):
        if self.proxy_list is None:
            self.proxy_list = []


class ConfigManager:
    """Advanced configuration management"""
    
    def __init__(self, config_path: str = "crawler_config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[CrawlerConfig] = None
    
    def create_default_config(self) -> CrawlerConfig:
        """Create a default configuration"""
        search_config = SearchConfig(
            keywords=["fashion", "穿搭"],
            min_likes=50,
            content_types=["image", "video"]
        )
        
        download_config = DownloadConfig(
            max_concurrent_downloads=3,
            min_image_resolution=(720, 720)
        )
        
        filter_config = FilterConfig(
            enable_duplicate_detection=True,
            similarity_threshold=0.85
        )
        
        export_config = ExportConfig(
            output_format="excel",
            create_html_gallery=True
        )
        
        return CrawlerConfig(
            search=search_config,
            download=download_config,
            filters=filter_config,
            export=export_config
        )
    
    def save_config(self, config: CrawlerConfig):
        """Save configuration to file"""
        config_dict = asdict(config)
        
        # Convert tuples to lists for YAML serialization
        def convert_tuples(obj):
            if isinstance(obj, dict):
                return {k: convert_tuples(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_tuples(item) for item in obj]
            elif isinstance(obj, tuple):
                return list(obj)
            else:
                return obj
        
        config_dict = convert_tuples(config_dict)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    def load_config(self) -> CrawlerConfig:
        """Load configuration from file"""
        if not self.config_path.exists():
            self.config = self.create_default_config()
            self.save_config(self.config)
            return self.config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # Convert lists back to tuples where needed
        def convert_lists_to_tuples(obj, keys_to_convert):
            if isinstance(obj, dict):
                for key in keys_to_convert:
                    if key in obj and isinstance(obj[key], list):
                        obj[key] = tuple(obj[key])
                return obj
            return obj
        
        # Convert specific list fields back to tuples
        tuple_fields = ['min_image_resolution', 'target_resolution']
        if 'download' in config_dict:
            convert_lists_to_tuples(config_dict['download'], tuple_fields)
        
        # Reconstruct nested dataclass objects
        search_config = SearchConfig(**config_dict['search'])
        download_config = DownloadConfig(**config_dict['download'])
        filter_config = FilterConfig(**config_dict['filters'])
        export_config = ExportConfig(**config_dict['export'])
        
        self.config = CrawlerConfig(
            search=search_config,
            download=download_config,
            filters=filter_config,
            export=export_config,
            **{k: v for k, v in config_dict.items() 
               if k not in ['search', 'download', 'filters', 'export']}
        )
        
        return self.config
    
    def update_config(self, **kwargs):
        """Update specific configuration values"""
        if self.config is None:
            self.config = self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self.save_config(self.config)
    
    def create_profile(self, profile_name: str, config: CrawlerConfig):
        """Save a named configuration profile"""
        profile_path = self.config_path.parent / f"{profile_name}_config.yaml"
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(config), f, default_flow_style=False, allow_unicode=True)
    
    def load_profile(self, profile_name: str) -> CrawlerConfig:
        """Load a named configuration profile"""
        profile_path = self.config_path.parent / f"{profile_name}_config.yaml"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        # Use the same loading logic as load_config
        temp_path = self.config_path
        self.config_path = profile_path
        config = self.load_config()
        self.config_path = temp_path
        
        return config


class SearchPresets:
    """Predefined search configurations for common use cases"""
    
    @staticmethod
    def fashion_trends() -> SearchConfig:
        return SearchConfig(
            keywords=["穿搭", "时尚", "outfit", "fashion", "OOTD"],
            hashtags=["#穿搭", "#时尚", "#OOTD"],
            min_likes=100,
            content_types=["image"],
            categories=["fashion", "lifestyle"]
        )
    
    @staticmethod
    def food_content() -> SearchConfig:
        return SearchConfig(
            keywords=["美食", "食谱", "cooking", "recipe"],
            hashtags=["#美食", "#食谱", "#cooking"],
            min_likes=50,
            content_types=["image", "video"],
            categories=["food", "cooking"]
        )
    
    @staticmethod
    def travel_content() -> SearchConfig:
        return SearchConfig(
            keywords=["旅行", "travel", "景点", "destination"],
            hashtags=["#旅行", "#travel", "#景点"],
            min_likes=75,
            content_types=["image", "video"],
            categories=["travel", "photography"]
        )
    
    @staticmethod
    def beauty_content() -> SearchConfig:
        return SearchConfig(
            keywords=["化妆", "美妆", "makeup", "beauty"],
            hashtags=["#化妆", "#美妆", "#makeup"],
            min_likes=100,
            content_types=["image", "video"],
            categories=["beauty", "makeup"]
        )


class AnalyticsConfig:
    """Configuration for analytics and reporting"""
    
    def __init__(self):
        self.track_trends = True
        self.generate_reports = True
        self.export_analytics = True
        self.sentiment_analysis = False
        self.engagement_tracking = True
        self.user_growth_tracking = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'track_trends': self.track_trends,
            'generate_reports': self.generate_reports,
            'export_analytics': self.export_analytics,
            'sentiment_analysis': self.sentiment_analysis,
            'engagement_tracking': self.engagement_tracking,
            'user_growth_tracking': self.user_growth_tracking
        }


# Example usage and testing
if __name__ == "__main__":
    # Create and test configuration manager
    config_manager = ConfigManager("test_config.yaml")
    
    # Create a fashion-focused configuration
    fashion_config = CrawlerConfig(
        search=SearchPresets.fashion_trends(),
        download=DownloadConfig(max_concurrent_downloads=5),
        filters=FilterConfig(enable_duplicate_detection=True),
        export=ExportConfig(create_html_gallery=True)
    )
    
    # Save configuration
    config_manager.save_config(fashion_config)
    print("✓ Configuration saved successfully")
    
    # Load and verify
    loaded_config = config_manager.load_config()
    print(f"✓ Loaded config with {len(loaded_config.search.keywords)} keywords")
    
    # Create profile
    config_manager.create_profile("fashion_trends", fashion_config)
    print("✓ Fashion trends profile created")