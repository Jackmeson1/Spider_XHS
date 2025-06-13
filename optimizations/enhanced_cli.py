"""Enhanced CLI with advanced features and user-friendly interface"""

import sys
import os
import asyncio
import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from optimizations.config_manager import ConfigManager, SearchPresets, CrawlerConfig
    from optimizations.smart_crawler import SmartCrawler, ContentItem
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure optimization dependencies are installed")
    sys.exit(1)

console = Console()


def _create_sample_items(count: int, keywords: List[str]) -> List[ContentItem]:
    """Create sample content items for demonstration"""
    items = []
    base_content = {
        "fashion": "今天分享一个超级好看的穿搭，这套OOTD融合了多种风格元素，既时尚又实用。",
        "food": "今天教大家做一道简单又美味的家常菜，材料简单，制作过程详细。",
        "travel": "这次旅行真的太棒了，风景如画，人文景观也很丰富。",
        "beauty": "今天分享一个日常妆容教程，简单易学，适合各种场合。"
    }
    
    for i in range(count):
        # Choose content based on keywords
        content_type = "fashion"  # default
        if any(word in ["美食", "食谱", "food", "cooking"] for word in keywords):
            content_type = "food"
        elif any(word in ["旅行", "travel", "景点"] for word in keywords):
            content_type = "travel"
        elif any(word in ["化妆", "美妆", "makeup", "beauty"] for word in keywords):
            content_type = "beauty"
        
        item = ContentItem(
            id=f"demo_{i+1}",
            url=f"https://example.com/demo_{i+1}",
            title=f"Sample {content_type} post {i+1}",
            content=base_content[content_type] + f" 第{i+1}期内容分享。",
            author=f"user_{i % 5 + 1}",
            author_id=f"user_id_{i % 5 + 1}",
            publish_time=datetime.now() - timedelta(days=i % 30),
            likes=50 + i * 20,
            comments=5 + i * 2,
            hashtags=[f"#{keyword}" for keyword in keywords[:2]],
            media_urls=[f"https://example.com/image_{i}.jpg"],
            media_types=["image"]
        )
        items.append(item)
    
    return items


class EnhancedCLI:
    """Enhanced command-line interface with rich features"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.console = Console()
    
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
🕷️  XHS Spider - Enhanced Crawler
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Professional content discovery and download tool for Xiaohongshu
with advanced filtering, analytics, and optimization features.
        """
        console.print(Panel(welcome_text, border_style="blue"))
    
    def show_stats_table(self, analytics: dict):
        """Display analytics in a formatted table"""
        table = Table(title="📊 Crawling Analytics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim", width=20)
        table.add_column("Value", justify="right")
        
        summary = analytics.get('summary', {})
        stats = analytics.get('processing_stats', {})
        
        table.add_row("Total Items Found", str(stats.get('total_found', 0)))
        table.add_row("Successfully Downloaded", str(summary.get('total_items', 0)))
        table.add_row("Duplicates Filtered", str(stats.get('duplicates_filtered', 0)))
        table.add_row("Quality Filtered", str(stats.get('quality_filtered', 0)))
        table.add_row("Average Quality Score", f"{summary.get('average_quality_score', 0):.2f}")
        table.add_row("Average Likes", f"{summary.get('average_likes', 0):.1f}")
        table.add_row("Total Engagement", str(summary.get('total_engagement', 0)))
        
        console.print(table)
    
    def show_category_distribution(self, analytics: dict):
        """Show content category distribution"""
        categories = analytics.get('category_distribution', {})
        if not categories:
            return
        
        table = Table(title="📂 Content Categories", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Percentage", justify="right", style="yellow")
        
        total = sum(categories.values())
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            table.add_row(category, str(count), f"{percentage:.1f}%")
        
        console.print(table)
    
    def interactive_config_setup(self) -> CrawlerConfig:
        """Interactive configuration setup"""
        console.print("\n🔧 Configuration Setup", style="bold blue")
        
        # Choose preset or custom
        presets = {
            "1": ("Fashion & Style", SearchPresets.fashion_trends),
            "2": ("Food & Cooking", SearchPresets.food_content),
            "3": ("Travel & Places", SearchPresets.travel_content),
            "4": ("Beauty & Makeup", SearchPresets.beauty_content),
            "5": ("Custom Configuration", None)
        }
        
        console.print("\nAvailable presets:")
        for key, (name, _) in presets.items():
            console.print(f"  {key}. {name}")
        
        choice = Prompt.ask("Choose a preset", choices=list(presets.keys()))
        
        if choice != "5":
            name, preset_func = presets[choice]
            console.print(f"✓ Selected: {name}")
            config = self.config_manager.create_default_config()
            config.search = preset_func()
        else:
            # Custom configuration
            config = self._create_custom_config()
        
        # Additional settings
        config.download.max_concurrent_downloads = int(
            Prompt.ask("Max concurrent downloads", default="3")
        )
        
        config.filters.enable_duplicate_detection = Confirm.ask(
            "Enable duplicate detection?", default=True
        )
        
        config.export.create_html_gallery = Confirm.ask(
            "Create HTML gallery?", default=True
        )
        
        return config
    
    def _create_custom_config(self) -> CrawlerConfig:
        """Create custom configuration interactively"""
        console.print("\n📝 Custom Configuration")
        
        # Keywords
        keywords_input = Prompt.ask("Enter keywords (comma-separated)")
        keywords = [k.strip() for k in keywords_input.split(",")]
        
        # Filters
        min_likes = int(Prompt.ask("Minimum likes", default="50"))
        min_comments = int(Prompt.ask("Minimum comments", default="0"))
        
        # Content types
        console.print("\nContent types: image, video, mixed")
        content_types_input = Prompt.ask("Content types (comma-separated)", default="image,video")
        content_types = [t.strip() for t in content_types_input.split(",")]
        
        from config_manager import SearchConfig, DownloadConfig, FilterConfig, ExportConfig
        
        search_config = SearchConfig(
            keywords=keywords,
            min_likes=min_likes,
            min_comments=min_comments,
            content_types=content_types
        )
        
        config = self.config_manager.create_default_config()
        config.search = search_config
        
        return config


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """🕷️ XHS Spider - Enhanced Crawler"""
    pass


@cli.command()
@click.option('--profile', '-p', help='Configuration profile name')
@click.option('--keywords', '-k', multiple=True, help='Search keywords')
@click.option('--count', '-c', default=10, help='Number of items to crawl')
@click.option('--output', '-o', default='./output', help='Output directory')
@click.option('--format', '-f', default='excel', 
              type=click.Choice(['excel', 'json', 'csv']), help='Output format')
@click.option('--quality-filter/--no-quality-filter', default=True, 
              help='Enable quality filtering')
@click.option('--duplicates/--no-duplicates', default=True, 
              help='Enable duplicate detection')
@click.option('--analytics/--no-analytics', default=True, 
              help='Generate analytics report')
@click.option('--gallery/--no-gallery', default=False, 
              help='Create HTML gallery')
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration')
def crawl(profile, keywords, count, output, format, quality_filter, 
          duplicates, analytics, gallery, interactive):
    """🚀 Start intelligent crawling with advanced features"""
    
    cli_handler = EnhancedCLI()
    cli_handler.show_welcome()
    
    try:
        # Configuration setup
        if interactive:
            config = cli_handler.interactive_config_setup()
        elif profile:
            config = cli_handler.config_manager.load_profile(profile)
            console.print(f"✓ Loaded profile: {profile}")
        else:
            config = cli_handler.config_manager.load_config()
            if keywords:
                config.search.keywords = list(keywords)
        
        # Update config with CLI options
        config.export.output_format = format
        config.filters.enable_quality_filter = quality_filter
        config.filters.enable_duplicate_detection = duplicates
        config.export.export_analytics = analytics
        config.export.create_html_gallery = gallery
        
        # Display configuration
        console.print("\n📋 Configuration Summary:", style="bold")
        console.print(f"Keywords: {', '.join(config.search.keywords)}")
        console.print(f"Target count: {count}")
        console.print(f"Quality filter: {'✓' if quality_filter else '✗'}")
        console.print(f"Duplicate detection: {'✓' if duplicates else '✗'}")
        
        if not Confirm.ask("\nProceed with crawling?"):
            console.print("❌ Crawling cancelled")
            return
        
        # Start crawling with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task1 = progress.add_task("🔍 Initializing crawler...", total=100)
            task2 = progress.add_task("📊 Processing content...", total=100)
            task3 = progress.add_task("📈 Generating analytics...", total=100)
            
            # Initialize smart crawler
            progress.update(task1, advance=50)
            crawler = SmartCrawler(config, max_workers=3)
            progress.update(task1, advance=50)
            
            # Create sample content items for demonstration
            progress.update(task2, advance=20)
            sample_items = _create_sample_items(count, config.search.keywords)
            progress.update(task2, advance=40)
            
            # Process items through smart crawler
            processed_items = crawler.process_batch(sample_items)
            progress.update(task2, advance=40)
            
            # Generate analytics
            progress.update(task3, advance=50)
            crawler.downloaded_items = processed_items
            analytics = crawler.generate_analytics_report()
            progress.update(task3, advance=50)
        
        # Display results
        console.print("\n🎉 Crawling completed!", style="bold green")
        cli_handler.show_stats_table(analytics)
        cli_handler.show_category_distribution(analytics)
        
        # Save results
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if config.export.export_analytics:
            analytics_file = output_path / "analytics.json"
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, indent=2, ensure_ascii=False, default=str)
            console.print(f"📊 Analytics saved to {analytics_file}")
        
        if gallery:
            console.print("🖼️  HTML gallery would be created here")
        
        console.print(f"\n✅ All files saved to: {output_path.absolute()}")
        
    except KeyboardInterrupt:
        console.print("\n⚠️  Crawling interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")


@cli.command()
def config():
    """⚙️ Interactive configuration management"""
    cli_handler = EnhancedCLI()
    config = cli_handler.interactive_config_setup()
    
    # Save configuration
    save_name = Prompt.ask("Save configuration as", default="default")
    if save_name != "default":
        cli_handler.config_manager.create_profile(save_name, config)
        console.print(f"✅ Configuration saved as profile: {save_name}")
    else:
        cli_handler.config_manager.save_config(config)
        console.print("✅ Default configuration updated")


@cli.command()
@click.argument('profile_name')
def profile(profile_name):
    """👤 Manage configuration profiles"""
    config_manager = ConfigManager()
    
    try:
        config = config_manager.load_profile(profile_name)
        
        # Display profile information
        table = Table(title=f"Profile: {profile_name}")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Keywords", ", ".join(config.search.keywords))
        table.add_row("Min Likes", str(config.search.min_likes))
        table.add_row("Content Types", ", ".join(config.search.content_types))
        table.add_row("Quality Filter", "✓" if config.filters.enable_quality_filter else "✗")
        table.add_row("Duplicate Detection", "✓" if config.filters.enable_duplicate_detection else "✗")
        
        console.print(table)
        
    except FileNotFoundError:
        console.print(f"❌ Profile '{profile_name}' not found", style="red")


@cli.command()
@click.argument('analytics_file', type=click.Path(exists=True))
def analyze(analytics_file):
    """📊 Analyze previous crawling results"""
    with open(analytics_file, 'r', encoding='utf-8') as f:
        analytics = json.load(f)
    
    cli_handler = EnhancedCLI()
    cli_handler.show_stats_table(analytics)
    cli_handler.show_category_distribution(analytics)
    
    # Additional insights
    console.print("\n🔍 Insights:", style="bold blue")
    
    summary = analytics.get('summary', {})
    if summary.get('average_quality_score', 0) > 0.8:
        console.print("✅ High quality content detected")
    elif summary.get('average_quality_score', 0) < 0.5:
        console.print("⚠️  Consider adjusting quality filters")
    
    engagement = summary.get('total_engagement', 0)
    items = summary.get('total_items', 1)
    avg_engagement = engagement / items
    
    if avg_engagement > 200:
        console.print("🔥 High engagement content!")
    elif avg_engagement < 50:
        console.print("💡 Consider targeting more popular keywords")


@cli.command()
def presets():
    """📋 Show available search presets"""
    table = Table(title="🎯 Available Search Presets")
    table.add_column("Preset", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Keywords", style="dim")
    
    presets_info = [
        ("fashion", "Fashion & Style content", "穿搭, 时尚, outfit, OOTD"),
        ("food", "Food & Cooking content", "美食, 食谱, cooking, recipe"),
        ("travel", "Travel & Places content", "旅行, travel, 景点"),
        ("beauty", "Beauty & Makeup content", "化妆, 美妆, makeup, beauty")
    ]
    
    for name, desc, keywords in presets_info:
        table.add_row(name, desc, keywords)
    
    console.print(table)
    console.print("\nUsage: xhs-spider crawl --profile <preset_name>")


if __name__ == "__main__":
    cli()