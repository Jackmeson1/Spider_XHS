#!/usr/bin/env python3
"""Demo script showcasing XHS Spider optimizations"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 XHS Spider Optimization Demo")
print("=" * 50)

try:
    from optimizations.config_manager import (
        ConfigManager, SearchPresets, CrawlerConfig
    )
    from optimizations.smart_crawler import (
        SmartCrawler, ContentItem, DuplicateDetector, ContentQualityAnalyzer
    )
    print("✅ Successfully imported optimization modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all optimization dependencies are installed:")
    print("pip install pyyaml scikit-learn pillow imagehash rich click aiohttp aiofiles")
    sys.exit(1)

def demo_configuration_management():
    """Demonstrate configuration management features"""
    print("\n🔧 Configuration Management Demo")
    print("-" * 30)
    
    # Create configuration manager
    config_manager = ConfigManager("demo_config.yaml")
    
    # Test default configuration
    config = config_manager.create_default_config()
    print(f"✓ Default config created with {len(config.search.keywords)} keywords")
    
    # Test search presets
    fashion_config = SearchPresets.fashion_trends()
    print(f"✓ Fashion preset: {len(fashion_config.keywords)} keywords, min_likes: {fashion_config.min_likes}")
    
    food_config = SearchPresets.food_content()
    print(f"✓ Food preset: {len(food_config.keywords)} keywords")
    
    # Save and load configuration
    config.search = fashion_config
    config_manager.save_config(config)
    print("✓ Configuration saved to demo_config.yaml")
    
    loaded_config = config_manager.load_config()
    print(f"✓ Configuration loaded: {len(loaded_config.search.keywords)} keywords")
    
    return config

def demo_duplicate_detection():
    """Demonstrate duplicate detection capabilities"""
    print("\n🔍 Duplicate Detection Demo")
    print("-" * 30)
    
    detector = DuplicateDetector(similarity_threshold=0.85)
    
    # Test text duplicate detection
    original_text = "今天分享一个超棒的穿搭，这套look非常适合春天！"
    duplicate_text = "今天分享一个超棒的穿搭，这套look非常适合春天！"
    different_text = "这是一个完全不同的内容，讲的是美食制作。"
    
    print("Testing text duplicate detection:")
    print(f"  Original text: {original_text[:30]}...")
    
    is_original_duplicate = detector.is_duplicate_text(original_text)
    print(f"  ✓ Original text duplicate: {is_original_duplicate}")
    
    is_duplicate = detector.is_duplicate_text(duplicate_text)
    print(f"  ✓ Exact duplicate detected: {is_duplicate}")
    
    is_different_duplicate = detector.is_duplicate_text(different_text)
    print(f"  ✓ Different text duplicate: {is_different_duplicate}")
    
    return detector

def demo_quality_analysis():
    """Demonstrate content quality analysis"""
    print("\n📊 Content Quality Analysis Demo")
    print("-" * 30)
    
    analyzer = ContentQualityAnalyzer()
    
    # Test different quality levels
    test_contents = [
        {
            "content": "今天分享一个非常详细的穿搭教程，这套look融合了韩系和日系的风格特点，既保持了韩系的简约大方，又融入了日系的精致细节。整套搭配以米色为主调，营造出温柔知性的氛围。",
            "likes": 500,
            "comments": 45,
            "label": "High Quality"
        },
        {
            "content": "今天的穿搭分享，希望大家喜欢这套look",
            "likes": 80,
            "comments": 8,
            "label": "Medium Quality"
        },
        {
            "content": "关注我，私信回复获取更多",
            "likes": 5,
            "comments": 1,
            "label": "Low Quality (Spam)"
        }
    ]
    
    for test in test_contents:
        text_score = analyzer.score_text_quality(test["content"])
        engagement_score = analyzer.score_engagement_quality(test["likes"], test["comments"])
        
        print(f"  {test['label']}:")
        print(f"    Text score: {text_score:.2f}")
        print(f"    Engagement score: {engagement_score:.2f}")
        print(f"    Content preview: {test['content'][:40]}...")
        print()
    
    return analyzer

def demo_smart_crawler():
    """Demonstrate smart crawler functionality"""
    print("\n🤖 Smart Crawler Demo")
    print("-" * 30)
    
    # Create configuration
    config_manager = ConfigManager()
    config = config_manager.create_default_config()
    config.search = SearchPresets.fashion_trends()
    config.filters.enable_duplicate_detection = True
    config.filters.enable_quality_filter = True
    config.filters.quality_threshold = 0.3  # Lower threshold for demo
    
    # Create sample content items
    sample_items = [
        ContentItem(
            id="fashion_1",
            url="https://example.com/fashion_1",
            title="时尚穿搭分享",
            content="今天分享一个超级棒的春季穿搭，这套OOTD融合了多种风格元素，既时尚又实用。整体以清新的色调为主，非常适合日常通勤。",
            author="fashion_blogger",
            author_id="fb123",
            publish_time=datetime.now(),
            likes=300,
            comments=35,
            hashtags=["#穿搭", "#时尚", "#OOTD", "#春季搭配"]
        ),
        ContentItem(
            id="fashion_2",
            url="https://example.com/fashion_2",
            title="重复内容测试",
            content="今天分享一个超级棒的春季穿搭，这套OOTD融合了多种风格元素，既时尚又实用。整体以清新的色调为主，非常适合日常通勤。",  # Exact duplicate
            author="copy_user",
            author_id="cu456",
            publish_time=datetime.now(),
            likes=50,
            comments=5,
            hashtags=["#穿搭"]
        ),
        ContentItem(
            id="food_1",
            url="https://example.com/food_1",
            title="美食制作",
            content="今天教大家做一道简单又美味的家常菜，材料简单，制作过程详细，新手也能轻松掌握。",
            author="food_lover",
            author_id="fl789",
            publish_time=datetime.now(),
            likes=150,
            comments=20,
            hashtags=["#美食", "#cooking", "#家常菜"]
        ),
        ContentItem(
            id="spam_1",
            url="https://example.com/spam_1",
            title="低质量内容",
            content="点击关注，私信回复1获取更多资源",
            author="spam_user",
            author_id="su000",
            publish_time=datetime.now(),
            likes=3,
            comments=0,
            hashtags=[]
        ),
        ContentItem(
            id="old_content",
            url="https://example.com/old",
            title="过期内容",
            content="这是一个很久之前的内容，可能已经不太相关了",
            author="old_user",
            author_id="ou111",
            publish_time=datetime.now() - timedelta(days=400),  # Very old
            likes=100,
            comments=10,
            hashtags=["#过期"]
        )
    ]
    
    # Create smart crawler and process items
    crawler = SmartCrawler(config, max_workers=1)
    
    print(f"📥 Processing {len(sample_items)} sample items...")
    print()
    
    processed_items = crawler.process_batch(sample_items)
    
    print(f"📊 Processing Results:")
    print(f"  Input items: {len(sample_items)}")
    print(f"  Output items: {len(processed_items)}")
    print(f"  Duplicates filtered: {crawler.stats['duplicates_filtered']}")
    print(f"  Quality filtered: {crawler.stats['quality_filtered']}")
    print()
    
    # Show categorization results
    print("📂 Categorization Results:")
    for item in processed_items:
        print(f"  {item.id}: {', '.join(item.categories)} (Quality: {item.quality_score:.2f})")
    print()
    
    # Generate analytics
    crawler.downloaded_items = processed_items
    analytics = crawler.generate_analytics_report()
    
    print("📈 Analytics Summary:")
    summary = analytics['summary']
    print(f"  Total items: {summary['total_items']}")
    print(f"  Average quality: {summary['average_quality_score']:.2f}")
    print(f"  Average likes: {summary['average_likes']:.1f}")
    print(f"  Total engagement: {summary['total_engagement']}")
    
    if analytics['category_distribution']:
        print(f"  Categories: {', '.join(analytics['category_distribution'].keys())}")
    
    return crawler, analytics

def demo_export_features():
    """Demonstrate export and analytics features"""
    print("\n📤 Export Features Demo")
    print("-" * 30)
    
    # Create output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create sample analytics data
    sample_analytics = {
        'summary': {
            'total_items': 25,
            'average_quality_score': 0.72,
            'average_likes': 156.3,
            'average_comments': 18.4,
            'total_engagement': 4357
        },
        'category_distribution': {
            'fashion': 15,
            'food': 7,
            'beauty': 3
        },
        'top_authors': [
            ('fashion_expert', 8),
            ('food_blogger', 5),
            ('style_guru', 4)
        ],
        'processing_stats': {
            'total_found': 35,
            'duplicates_filtered': 6,
            'quality_filtered': 4,
            'successfully_downloaded': 25
        },
        'quality_breakdown': {
            'high_quality': 8,
            'medium_quality': 12,
            'low_quality': 5
        }
    }
    
    # Export analytics to JSON
    import json
    analytics_file = output_dir / "demo_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(sample_analytics, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Analytics exported to {analytics_file}")
    
    # Create a simple HTML gallery template
    categories_html = ''.join([f'<span class="category">{cat}: {count}</span>' 
                              for cat, count in sample_analytics['category_distribution'].items()])
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>XHS Spider Analytics Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px; border-radius: 5px; }}
        .category {{ display: inline-block; margin: 5px; padding: 5px 10px; background: #e3f2fd; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>📊 XHS Spider Analytics Dashboard</h1>
    
    <div class="metric">
        <h3>Summary</h3>
        <p>Total Items: {sample_analytics['summary']['total_items']}</p>
        <p>Average Quality: {sample_analytics['summary']['average_quality_score']:.2f}</p>
        <p>Total Engagement: {sample_analytics['summary']['total_engagement']}</p>
    </div>
    
    <div class="metric">
        <h3>Categories</h3>
        {categories_html}
    </div>
    
    <div class="metric">
        <h3>Processing Stats</h3>
        <p>Found: {sample_analytics['processing_stats']['total_found']}</p>
        <p>Duplicates Filtered: {sample_analytics['processing_stats']['duplicates_filtered']}</p>
        <p>Quality Filtered: {sample_analytics['processing_stats']['quality_filtered']}</p>
    </div>
</body>
</html>"""
    
    html_file = output_dir / "demo_dashboard.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ HTML dashboard created at {html_file}")
    
    return analytics_file, html_file

def main():
    """Run the complete optimization demo"""
    print("Starting comprehensive optimization demo...\n")
    
    try:
        # 1. Configuration Management
        config = demo_configuration_management()
        
        # 2. Duplicate Detection
        detector = demo_duplicate_detection()
        
        # 3. Quality Analysis
        analyzer = demo_quality_analysis()
        
        # 4. Smart Crawler
        crawler, analytics = demo_smart_crawler()
        
        # 5. Export Features
        analytics_file, html_file = demo_export_features()
        
        print("\n🎉 Demo Completed Successfully!")
        print("=" * 50)
        print("✅ All optimization features demonstrated:")
        print("   • Configuration management with presets")
        print("   • Intelligent duplicate detection")
        print("   • Content quality analysis")
        print("   • Smart crawler with filtering")
        print("   • Analytics generation")
        print("   • Export capabilities")
        print()
        print("📁 Output files created:")
        print(f"   • Configuration: demo_config.yaml")
        print(f"   • Analytics: {analytics_file}")
        print(f"   • Dashboard: {html_file}")
        print()
        print("🚀 The optimization system is ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)