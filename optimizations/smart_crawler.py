"""Smart crawler with advanced features and optimizations"""

import asyncio
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json

import aiohttp
import aiofiles
from PIL import Image
import imagehash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class ContentItem:
    """Enhanced content item with metadata"""
    id: str
    url: str
    title: str
    content: str
    author: str
    author_id: str
    publish_time: datetime
    likes: int = 0
    comments: int = 0
    shares: int = 0
    media_urls: List[str] = None
    media_types: List[str] = None
    hashtags: List[str] = None
    categories: List[str] = None
    sentiment_score: float = 0.0
    quality_score: float = 0.0
    duplicate_hash: str = ""
    
    def __post_init__(self):
        if self.media_urls is None:
            self.media_urls = []
        if self.media_types is None:
            self.media_types = []
        if self.hashtags is None:
            self.hashtags = []
        if self.categories is None:
            self.categories = []


class DuplicateDetector:
    """Advanced duplicate detection using multiple methods"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.text_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.seen_hashes: Set[str] = set()
        self.image_hashes: Dict[str, str] = {}
    
    def compute_text_hash(self, content: str) -> str:
        """Compute hash for text content"""
        normalized = content.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def compute_image_hash(self, image_path: str) -> str:
        """Compute perceptual hash for images"""
        try:
            with Image.open(image_path) as img:
                return str(imagehash.phash(img))
        except Exception:
            return ""
    
    def is_duplicate_text(self, content: str) -> bool:
        """Check if text content is duplicate"""
        text_hash = self.compute_text_hash(content)
        if text_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(text_hash)
        return False
    
    def is_duplicate_image(self, image_path: str, content_id: str) -> bool:
        """Check if image is duplicate using perceptual hashing"""
        img_hash = self.compute_image_hash(image_path)
        if not img_hash:
            return False
        
        # Check against existing hashes
        for existing_id, existing_hash in self.image_hashes.items():
            if existing_id != content_id:
                # Compare hashes (lower difference = more similar)
                diff = bin(int(img_hash, 16) ^ int(existing_hash, 16)).count('1')
                if diff < 5:  # Very similar images
                    return True
        
        self.image_hashes[content_id] = img_hash
        return False
    
    def compute_content_similarity(self, contents: List[str]) -> List[List[float]]:
        """Compute text similarity matrix"""
        if len(contents) < 2:
            return [[1.0]]
        
        tfidf_matrix = self.text_vectorizer.fit_transform(contents)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix.tolist()


class ContentQualityAnalyzer:
    """Analyze and score content quality"""
    
    def __init__(self):
        self.min_content_length = 10
        self.min_image_resolution = (500, 500)
    
    def score_text_quality(self, content: str) -> float:
        """Score text content quality (0-1)"""
        score = 0.0
        
        # Length score
        if len(content) >= self.min_content_length:
            score += 0.3
        
        # Character variety score
        unique_chars = len(set(content.lower()))
        if unique_chars > 10:
            score += 0.2
        
        # Word count score
        words = content.split()
        if len(words) >= 5:
            score += 0.2
        
        # No spam indicators
        spam_indicators = ['点击', '关注', '私信', 'follow', 'click']
        spam_count = sum(1 for indicator in spam_indicators if indicator in content.lower())
        if spam_count == 0:
            score += 0.3
        elif spam_count == 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def score_engagement_quality(self, likes: int, comments: int, views: int = 0) -> float:
        """Score based on engagement metrics"""
        if views == 0:
            views = max(likes * 10, 100)  # Estimate views
        
        engagement_rate = (likes + comments * 2) / views
        
        # Normalize to 0-1 scale
        if engagement_rate > 0.1:
            return 1.0
        elif engagement_rate > 0.05:
            return 0.8
        elif engagement_rate > 0.02:
            return 0.6
        elif engagement_rate > 0.01:
            return 0.4
        else:
            return 0.2
    
    def score_media_quality(self, media_path: str) -> float:
        """Score media quality"""
        try:
            if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                with Image.open(media_path) as img:
                    width, height = img.size
                    
                    # Resolution score
                    if width >= 1080 and height >= 1080:
                        return 1.0
                    elif width >= 720 and height >= 720:
                        return 0.8
                    elif width >= 500 and height >= 500:
                        return 0.6
                    else:
                        return 0.3
            else:
                # For videos, assume good quality for now
                return 0.8
        except Exception:
            return 0.0
    
    def compute_overall_quality(self, item: ContentItem) -> float:
        """Compute overall quality score"""
        text_score = self.score_text_quality(item.content)
        engagement_score = self.score_engagement_quality(item.likes, item.comments)
        
        # Weight the scores
        overall_score = (text_score * 0.4 + engagement_score * 0.6)
        return overall_score


class SmartCrawler:
    """Enhanced crawler with intelligence and optimization"""
    
    def __init__(self, config, max_workers: int = 5):
        self.config = config
        self.max_workers = max_workers
        self.duplicate_detector = DuplicateDetector(config.filters.similarity_threshold)
        self.quality_analyzer = ContentQualityAnalyzer()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session = None
        self.downloaded_items: List[ContentItem] = []
        self.stats = {
            'total_found': 0,
            'duplicates_filtered': 0,
            'quality_filtered': 0,
            'successfully_downloaded': 0,
            'failed_downloads': 0
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.download.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.max_workers)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def categorize_content(self, item: ContentItem) -> List[str]:
        """Auto-categorize content based on keywords and hashtags"""
        categories = []
        content_lower = item.content.lower()
        hashtags_lower = [tag.lower() for tag in item.hashtags]
        
        # Fashion keywords
        fashion_keywords = ['穿搭', '时尚', 'outfit', 'fashion', 'ootd', '搭配']
        if any(keyword in content_lower for keyword in fashion_keywords) or \
           any(keyword in hashtags_lower for keyword in fashion_keywords):
            categories.append('fashion')
        
        # Food keywords
        food_keywords = ['美食', '食谱', 'food', 'recipe', 'cooking', '做菜']
        if any(keyword in content_lower for keyword in food_keywords) or \
           any(keyword in hashtags_lower for keyword in food_keywords):
            categories.append('food')
        
        # Travel keywords
        travel_keywords = ['旅行', 'travel', '景点', 'destination', '旅游']
        if any(keyword in content_lower for keyword in travel_keywords) or \
           any(keyword in hashtags_lower for keyword in travel_keywords):
            categories.append('travel')
        
        # Beauty keywords
        beauty_keywords = ['化妆', '美妆', 'makeup', 'beauty', '护肤']
        if any(keyword in content_lower for keyword in beauty_keywords) or \
           any(keyword in hashtags_lower for keyword in beauty_keywords):
            categories.append('beauty')
        
        return categories if categories else ['general']
    
    def filter_by_quality(self, item: ContentItem) -> bool:
        """Filter content by quality score"""
        if not self.config.filters.enable_quality_filter:
            return True
        
        quality_score = self.quality_analyzer.compute_overall_quality(item)
        item.quality_score = quality_score
        
        # Use a default threshold if not set
        threshold = getattr(self.config.filters, 'quality_threshold', 0.5)
        return quality_score >= threshold
    
    def filter_by_engagement(self, item: ContentItem) -> bool:
        """Filter by engagement thresholds"""
        return (item.likes >= self.config.search.min_likes and 
                item.comments >= self.config.search.min_comments)
    
    def filter_by_content_type(self, item: ContentItem) -> bool:
        """Filter by allowed content types"""
        if not self.config.search.content_types:
            return True
        
        has_images = any('image' in media_type for media_type in item.media_types)
        has_videos = any('video' in media_type for media_type in item.media_types)
        
        if 'image' in self.config.search.content_types and has_images:
            return True
        if 'video' in self.config.search.content_types and has_videos:
            return True
        if 'mixed' in self.config.search.content_types and has_images and has_videos:
            return True
        
        return False
    
    def should_include_content(self, item: ContentItem) -> bool:
        """Comprehensive content filtering"""
        # Check duplicates
        if self.config.filters.enable_duplicate_detection:
            if self.duplicate_detector.is_duplicate_text(item.content):
                self.stats['duplicates_filtered'] += 1
                return False
        
        # Check engagement
        if not self.filter_by_engagement(item):
            return False
        
        # Check content type
        if not self.filter_by_content_type(item):
            return False
        
        # Check quality
        if not self.filter_by_quality(item):
            self.stats['quality_filtered'] += 1
            return False
        
        # Check age
        if item.publish_time:
            max_age = datetime.now() - timedelta(days=self.config.search.max_age_days)
            if item.publish_time < max_age:
                return False
        
        return True
    
    async def download_media_async(self, url: str, output_path: Path) -> bool:
        """Asynchronously download media"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    return True
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
        return False
    
    def process_batch(self, items: List[ContentItem]) -> List[ContentItem]:
        """Process a batch of content items"""
        processed_items = []
        
        for item in items:
            self.stats['total_found'] += 1
            
            # Auto-categorize
            item.categories = self.categorize_content(item)
            
            # Apply filters
            if self.should_include_content(item):
                processed_items.append(item)
        
        return processed_items
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        total_items = len(self.downloaded_items)
        
        if total_items == 0:
            return {
                'summary': {
                    'total_items': 0,
                    'average_quality_score': 0,
                    'average_likes': 0,
                    'average_comments': 0,
                    'total_engagement': 0
                },
                'category_distribution': {},
                'top_authors': [],
                'time_distribution': {},
                'processing_stats': self.stats,
                'quality_breakdown': {
                    'high_quality': 0,
                    'medium_quality': 0,
                    'low_quality': 0
                }
            }
        
        # Category distribution
        category_counts = {}
        for item in self.downloaded_items:
            for category in item.categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Quality distribution
        quality_scores = [item.quality_score for item in self.downloaded_items if item.quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Engagement stats
        total_likes = sum(item.likes for item in self.downloaded_items)
        total_comments = sum(item.comments for item in self.downloaded_items)
        avg_likes = total_likes / total_items
        avg_comments = total_comments / total_items
        
        # Top authors
        author_counts = {}
        for item in self.downloaded_items:
            author_counts[item.author] = author_counts.get(item.author, 0) + 1
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Time distribution
        time_distribution = {}
        for item in self.downloaded_items:
            if item.publish_time:
                date_key = item.publish_time.strftime('%Y-%m-%d')
                time_distribution[date_key] = time_distribution.get(date_key, 0) + 1
        
        return {
            'summary': {
                'total_items': total_items,
                'average_quality_score': round(avg_quality, 2),
                'average_likes': round(avg_likes, 1),
                'average_comments': round(avg_comments, 1),
                'total_engagement': total_likes + total_comments
            },
            'category_distribution': category_counts,
            'top_authors': top_authors,
            'time_distribution': time_distribution,
            'processing_stats': self.stats,
            'quality_breakdown': {
                'high_quality': len([i for i in self.downloaded_items if i.quality_score >= 0.8]),
                'medium_quality': len([i for i in self.downloaded_items if 0.5 <= i.quality_score < 0.8]),
                'low_quality': len([i for i in self.downloaded_items if i.quality_score < 0.5])
            }
        }
    
    def export_analytics(self, output_path: str):
        """Export analytics to JSON file"""
        analytics = self.generate_analytics_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"Analytics exported to {output_path}")


# Example usage
async def example_smart_crawling():
    """Example of how to use the smart crawler"""
    from optimizations.config_manager import ConfigManager, SearchPresets
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    config.search = SearchPresets.fashion_trends()
    
    # Use smart crawler
    async with SmartCrawler(config, max_workers=3) as crawler:
        # Simulate some content items
        sample_items = [
            ContentItem(
                id="1",
                url="https://example.com/1",
                title="Fashion Post",
                content="今天的穿搭分享，很喜欢这个搭配",
                author="user1",
                author_id="123",
                publish_time=datetime.now(),
                likes=150,
                comments=20,
                hashtags=["#穿搭", "#时尚"]
            ),
            # Add more sample items...
        ]
        
        # Process items
        processed_items = crawler.process_batch(sample_items)
        crawler.downloaded_items = processed_items
        
        # Generate analytics
        analytics = crawler.generate_analytics_report()
        print("Analytics generated:", analytics['summary'])


if __name__ == "__main__":
    asyncio.run(example_smart_crawling())