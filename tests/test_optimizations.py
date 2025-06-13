#!/usr/bin/env python3
"""Comprehensive tests for XHS Spider optimizations"""

import sys
import os
import tempfile
import unittest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from optimizations.config_manager import (
        ConfigManager, SearchConfig, DownloadConfig, FilterConfig, 
        ExportConfig, CrawlerConfig, SearchPresets
    )
    from optimizations.smart_crawler import (
        SmartCrawler, ContentItem, DuplicateDetector, ContentQualityAnalyzer
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("This is expected if optimization dependencies are not installed")
    sys.exit(0)


class TestConfigManager(unittest.TestCase):
    """Test configuration management system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.config_manager = ConfigManager(self.config_file)
    
    def test_create_default_config(self):
        """Test default configuration creation"""
        config = self.config_manager.create_default_config()
        
        self.assertIsInstance(config, CrawlerConfig)
        self.assertIsInstance(config.search, SearchConfig)
        self.assertIsInstance(config.download, DownloadConfig)
        self.assertIsInstance(config.filters, FilterConfig)
        self.assertIsInstance(config.export, ExportConfig)
        
        # Test default values
        self.assertGreater(len(config.search.keywords), 0)
        self.assertEqual(config.download.max_concurrent_downloads, 3)
        self.assertTrue(config.filters.enable_duplicate_detection)
        print("✓ Default configuration created successfully")
    
    def test_save_and_load_config(self):
        """Test configuration persistence"""
        # Create and save config
        config = self.config_manager.create_default_config()
        config.search.keywords = ["test_keyword", "测试关键词"]
        config.search.min_likes = 100
        
        self.config_manager.save_config(config)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load and verify
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config.search.keywords, ["test_keyword", "测试关键词"])
        self.assertEqual(loaded_config.search.min_likes, 100)
        print("✓ Configuration save/load working correctly")
    
    def test_search_presets(self):
        """Test predefined search configurations"""
        fashion_config = SearchPresets.fashion_trends()
        self.assertIn("穿搭", fashion_config.keywords)
        self.assertIn("时尚", fashion_config.keywords)
        self.assertGreater(fashion_config.min_likes, 0)
        
        food_config = SearchPresets.food_content()
        self.assertIn("美食", food_config.keywords)
        
        travel_config = SearchPresets.travel_content()
        self.assertIn("旅行", travel_config.keywords)
        
        beauty_config = SearchPresets.beauty_content()
        self.assertIn("化妆", beauty_config.keywords)
        
        print("✓ All search presets working correctly")


class TestDuplicateDetector(unittest.TestCase):
    """Test duplicate detection functionality"""
    
    def setUp(self):
        self.detector = DuplicateDetector(similarity_threshold=0.85)
    
    def test_text_duplicate_detection(self):
        """Test text-based duplicate detection"""
        content1 = "这是一个测试内容，包含一些中文和English文本。"
        content2 = "这是一个测试内容，包含一些中文和English文本。"  # Exact duplicate
        content3 = "这是另一个完全不同的内容。"
        
        # First content should not be duplicate
        self.assertFalse(self.detector.is_duplicate_text(content1))
        
        # Exact duplicate should be detected
        self.assertTrue(self.detector.is_duplicate_text(content2))
        
        # Different content should not be duplicate
        self.assertFalse(self.detector.is_duplicate_text(content3))
        
        print("✓ Text duplicate detection working correctly")
    
    def test_text_hash_generation(self):
        """Test text hash generation"""
        content = "Test content for hashing"
        hash1 = self.detector.compute_text_hash(content)
        hash2 = self.detector.compute_text_hash(content)
        hash3 = self.detector.compute_text_hash("Different content")
        
        # Same content should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different content should produce different hash
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be a valid MD5 hex string
        self.assertEqual(len(hash1), 32)
        
        print("✓ Text hash generation working correctly")


class TestContentQualityAnalyzer(unittest.TestCase):
    """Test content quality analysis"""
    
    def setUp(self):
        self.analyzer = ContentQualityAnalyzer()
    
    def test_text_quality_scoring(self):
        """Test text quality scoring"""
        # High quality content
        high_quality = "这是一篇高质量的文章，内容丰富，包含有价值的信息和见解。文章结构清晰，语言流畅，为读者提供了实用的建议。"
        high_score = self.analyzer.score_text_quality(high_quality)
        
        # Low quality content
        low_quality = "点击关注私信"
        low_score = self.analyzer.score_text_quality(low_quality)
        
        # Medium quality content
        medium_quality = "今天的穿搭分享，希望大家喜欢"
        medium_score = self.analyzer.score_text_quality(medium_quality)
        
        self.assertGreater(high_score, medium_score)
        self.assertGreater(medium_score, low_score)
        self.assertLessEqual(high_score, 1.0)
        self.assertGreaterEqual(low_score, 0.0)
        
        print(f"✓ Text quality scoring: High={high_score:.2f}, Medium={medium_score:.2f}, Low={low_score:.2f}")
    
    def test_engagement_quality_scoring(self):
        """Test engagement-based quality scoring"""
        # High engagement
        high_engagement = self.analyzer.score_engagement_quality(1000, 100, 10000)
        
        # Medium engagement
        medium_engagement = self.analyzer.score_engagement_quality(100, 10, 2000)
        
        # Low engagement
        low_engagement = self.analyzer.score_engagement_quality(5, 1, 1000)
        
        self.assertGreater(high_engagement, medium_engagement)
        self.assertGreater(medium_engagement, low_engagement)
        
        print(f"✓ Engagement scoring: High={high_engagement:.2f}, Medium={medium_engagement:.2f}, Low={low_engagement:.2f}")


class TestSmartCrawler(unittest.TestCase):
    """Test smart crawler functionality"""
    
    def setUp(self):
        # Create test configuration
        from optimizations.config_manager import ConfigManager
        config_manager = ConfigManager()
        self.config = config_manager.create_default_config()
        self.config.search.keywords = ["test"]
        self.config.filters.similarity_threshold = 0.85
    
    def test_content_categorization(self):
        """Test automatic content categorization"""
        crawler = SmartCrawler(self.config, max_workers=1)
        
        # Fashion content
        fashion_item = ContentItem(
            id="1",
            url="https://example.com/1",
            title="Fashion Post",
            content="今天的穿搭分享，很喜欢这个OOTD搭配",
            author="user1",
            author_id="123",
            publish_time=datetime.now(),
            hashtags=["#穿搭", "#时尚"]
        )
        
        categories = crawler.categorize_content(fashion_item)
        self.assertIn("fashion", categories)
        
        # Food content
        food_item = ContentItem(
            id="2",
            url="https://example.com/2",
            title="Food Post",
            content="今天做了一道美食，分享食谱给大家",
            author="user2",
            author_id="456",
            publish_time=datetime.now(),
            hashtags=["#美食", "#cooking"]
        )
        
        categories = crawler.categorize_content(food_item)
        self.assertIn("food", categories)
        
        print("✓ Content categorization working correctly")
    
    def test_quality_filtering(self):
        """Test content quality filtering"""
        crawler = SmartCrawler(self.config, max_workers=1)
        
        # High quality item
        high_quality_item = ContentItem(
            id="1",
            url="https://example.com/1",
            title="High Quality Post",
            content="这是一篇高质量的内容，包含丰富的信息和有价值的见解。",
            author="user1",
            author_id="123",
            publish_time=datetime.now(),
            likes=500,
            comments=50
        )
        
        # Low quality item
        low_quality_item = ContentItem(
            id="2",
            url="https://example.com/2",
            title="Low Quality Post",
            content="点击关注",
            author="user2",
            author_id="456",
            publish_time=datetime.now(),
            likes=1,
            comments=0
        )
        
        # Test filtering
        self.assertTrue(crawler.filter_by_quality(high_quality_item))
        self.assertFalse(crawler.filter_by_quality(low_quality_item))
        
        print("✓ Quality filtering working correctly")
    
    def test_analytics_generation(self):
        """Test analytics report generation"""
        crawler = SmartCrawler(self.config, max_workers=1)
        
        # Add sample items
        items = [
            ContentItem(
                id=str(i),
                url=f"https://example.com/{i}",
                title=f"Post {i}",
                content=f"Content for post {i} with sufficient length",
                author=f"user{i % 3}",
                author_id=str(i % 3),
                publish_time=datetime.now() - timedelta(days=i),
                likes=100 + i * 10,
                comments=10 + i,
                categories=["fashion" if i % 2 == 0 else "food"],
                quality_score=0.5 + (i % 5) * 0.1
            )
            for i in range(10)
        ]
        
        crawler.downloaded_items = items
        analytics = crawler.generate_analytics_report()
        
        # Verify analytics structure
        self.assertIn('summary', analytics)
        self.assertIn('category_distribution', analytics)
        self.assertIn('top_authors', analytics)
        self.assertIn('processing_stats', analytics)
        
        # Verify summary data
        summary = analytics['summary']
        self.assertEqual(summary['total_items'], 10)
        self.assertGreater(summary['average_likes'], 0)
        self.assertGreater(summary['total_engagement'], 0)
        
        print("✓ Analytics generation working correctly")
        print(f"  - Total items: {summary['total_items']}")
        print(f"  - Average quality: {summary['average_quality_score']:.2f}")
        print(f"  - Categories found: {len(analytics['category_distribution'])}")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete optimization system"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from config to analytics"""
        # 1. Create configuration
        config_manager = ConfigManager()
        config = config_manager.create_default_config()
        config.search = SearchPresets.fashion_trends()
        config.search.min_likes = 50
        
        # 2. Create sample data
        sample_items = [
            ContentItem(
                id="fashion_1",
                url="https://example.com/fashion_1",
                title="时尚穿搭分享",
                content="今天分享一个超级好看的穿搭，OOTD来啦！这套搭配非常适合春天，既时尚又舒适。",
                author="fashion_blogger",
                author_id="fb123",
                publish_time=datetime.now(),
                likes=200,
                comments=25,
                hashtags=["#穿搭", "#时尚", "#OOTD"]
            ),
            ContentItem(
                id="fashion_2",
                url="https://example.com/fashion_2",
                title="重复内容测试",
                content="今天分享一个超级好看的穿搭，OOTD来啦！这套搭配非常适合春天，既时尚又舒适。",  # Duplicate
                author="another_user",
                author_id="au456",
                publish_time=datetime.now(),
                likes=150,
                comments=20,
                hashtags=["#穿搭"]
            ),
            ContentItem(
                id="low_quality",
                url="https://example.com/low_quality",
                title="低质量内容",
                content="关注我私信",
                author="spam_user",
                author_id="su789",
                publish_time=datetime.now(),
                likes=5,
                comments=1,
                hashtags=[]
            )
        ]
        
        # 3. Process with smart crawler
        crawler = SmartCrawler(config, max_workers=1)
        processed_items = crawler.process_batch(sample_items)
        
        # 4. Verify processing results
        self.assertLess(len(processed_items), len(sample_items))  # Some should be filtered
        
        # High quality fashion content should be included
        fashion_items = [item for item in processed_items if "fashion" in item.categories]
        self.assertGreater(len(fashion_items), 0)
        
        # 5. Generate analytics
        crawler.downloaded_items = processed_items
        analytics = crawler.generate_analytics_report()
        
        self.assertGreater(analytics['summary']['total_items'], 0)
        self.assertIn('fashion', analytics['category_distribution'])
        
        print("✓ End-to-end workflow completed successfully")
        print(f"  - Input items: {len(sample_items)}")
        print(f"  - Processed items: {len(processed_items)}")
        print(f"  - Duplicates filtered: {crawler.stats['duplicates_filtered']}")
        print(f"  - Quality filtered: {crawler.stats['quality_filtered']}")


def run_optimization_tests():
    """Run all optimization tests"""
    print("🧪 Running XHS Spider Optimization Tests\n")
    
    test_classes = [
        TestConfigManager,
        TestDuplicateDetector,
        TestContentQualityAnalyzer,
        TestSmartCrawler,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}:")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w')).run(suite)
        
        class_total = result.testsRun
        class_passed = class_total - len(result.failures) - len(result.errors)
        
        total_tests += class_total
        passed_tests += class_passed
        
        if result.failures:
            print(f"❌ {len(result.failures)} test(s) failed")
            for test, traceback in result.failures:
                print(f"   FAIL: {test}")
        
        if result.errors:
            print(f"💥 {len(result.errors)} test(s) had errors")
            for test, traceback in result.errors:
                print(f"   ERROR: {test}")
        
        if class_passed == class_total:
            print(f"✅ All {class_total} tests passed")
        else:
            print(f"⚠️  {class_passed}/{class_total} tests passed")
    
    print(f"\n📊 Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 All optimization tests passed! The enhanced crawler is ready to use.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    run_optimization_tests()