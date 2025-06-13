#!/usr/bin/env python3
"""Test script for enhanced CLI functionality"""

import subprocess
import json
from pathlib import Path
import os

def run_command(cmd, input_text=None):
    """Run a command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            input=input_text,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def test_cli_help():
    """Test CLI help commands"""
    print("🧪 Testing CLI Help Commands")
    
    # Test main help
    code, stdout, stderr = run_command("python3 optimizations/enhanced_cli.py --help")
    assert code == 0, f"Main help failed: {stderr}"
    assert "XHS Spider - Enhanced Crawler" in stdout
    print("✓ Main help working")
    
    # Test crawl help
    code, stdout, stderr = run_command("python3 optimizations/enhanced_cli.py crawl --help")
    assert code == 0, f"Crawl help failed: {stderr}"
    assert "Start intelligent crawling" in stdout
    print("✓ Crawl help working")

def test_presets():
    """Test presets command"""
    print("\n🧪 Testing Presets Command")
    
    code, stdout, stderr = run_command("python3 optimizations/enhanced_cli.py presets")
    assert code == 0, f"Presets failed: {stderr}"
    assert "fashion" in stdout
    assert "food" in stdout
    assert "travel" in stdout
    assert "beauty" in stdout
    print("✓ Presets command working")

def test_basic_crawl():
    """Test basic crawling functionality"""
    print("\n🧪 Testing Basic Crawl")
    
    # Clean up any existing test output
    test_dir = Path("./cli_test_output")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Test basic crawl with auto-confirmation
    cmd = 'python3 optimizations/enhanced_cli.py crawl --keywords "测试" --count 3 --output ./cli_test_output'
    code, stdout, stderr = run_command(cmd, input_text="y\n")
    
    print(f"Return code: {code}")
    print(f"Stdout: {stdout[:500]}...")
    print(f"Stderr: {stderr}")
    
    assert code == 0, f"Basic crawl failed: {stderr}"
    assert "Crawling completed!" in stdout
    
    # Check if output files were created
    analytics_file = test_dir / "analytics.json"
    assert analytics_file.exists(), "Analytics file not created"
    
    # Validate analytics content
    with open(analytics_file, 'r', encoding='utf-8') as f:
        analytics = json.load(f)
    
    assert 'summary' in analytics
    assert 'processing_stats' in analytics
    print("✓ Basic crawl working with analytics output")

def test_interactive_crawl():
    """Test interactive crawl mode"""
    print("\n🧪 Testing Interactive Crawl")
    
    # Test interactive mode with fashion preset
    cmd = 'python3 optimizations/enhanced_cli.py crawl --interactive --count 2 --output ./cli_test_interactive'
    input_text = "1\n3\ny\ny\ny\n"  # Choose fashion preset, keep defaults, proceed
    
    code, stdout, stderr = run_command(cmd, input_text=input_text)
    
    print(f"Return code: {code}")
    if code != 0:
        print(f"Stderr: {stderr}")
    
    assert code == 0, f"Interactive crawl failed: {stderr}"
    assert "Fashion & Style" in stdout
    assert "Crawling completed!" in stdout
    print("✓ Interactive crawl working")

def test_configuration_commands():
    """Test configuration-related commands"""
    print("\n🧪 Testing Configuration Commands")
    
    # Test config command (creates a profile)
    cmd = 'python3 optimizations/enhanced_cli.py config'
    input_text = "1\n3\ny\ny\ntest_profile\n"  # Fashion preset, save as test_profile
    
    code, stdout, stderr = run_command(cmd, input_text=input_text)
    assert code == 0, f"Config command failed: {stderr}"
    print("✓ Configuration creation working")
    
    # Test profile command (display profile info)
    code, stdout, stderr = run_command("python3 optimizations/enhanced_cli.py profile test_profile")
    if code == 0:
        assert "Profile: test_profile" in stdout
        print("✓ Profile display working")
    else:
        print("⚠️  Profile display not working (profile may not exist)")

def test_analytics_command():
    """Test analytics analysis command"""
    print("\n🧪 Testing Analytics Command")
    
    # Use the analytics file from basic crawl test
    analytics_file = "./cli_test_output/analytics.json"
    if Path(analytics_file).exists():
        code, stdout, stderr = run_command(f"python3 optimizations/enhanced_cli.py analyze {analytics_file}")
        assert code == 0, f"Analytics command failed: {stderr}"
        assert "Crawling Analytics" in stdout
        print("✓ Analytics analysis working")
    else:
        print("⚠️  Skipping analytics test (no analytics file found)")

def test_different_formats():
    """Test different output formats"""
    print("\n🧪 Testing Different Output Formats")
    
    # Test JSON format
    cmd = 'python3 optimizations/enhanced_cli.py crawl --keywords "json测试" --count 2 --format json --output ./cli_test_json'
    code, stdout, stderr = run_command(cmd, input_text="y\n")
    assert code == 0, f"JSON format failed: {stderr}"
    print("✓ JSON format working")
    
    # Test CSV format
    cmd = 'python3 optimizations/enhanced_cli.py crawl --keywords "csv测试" --count 2 --format csv --output ./cli_test_csv'
    code, stdout, stderr = run_command(cmd, input_text="y\n")
    assert code == 0, f"CSV format failed: {stderr}"
    print("✓ CSV format working")

def main():
    """Run all CLI tests"""
    print("🚀 Enhanced CLI Test Suite")
    print("=" * 50)
    
    try:
        test_cli_help()
        test_presets()
        test_basic_crawl()
        test_interactive_crawl()
        test_configuration_commands()
        test_analytics_command()
        test_different_formats()
        
        print("\n🎉 All CLI tests passed!")
        print("✅ Enhanced CLI is working correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)