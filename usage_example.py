#!/usr/bin/env python3
"""
YouTube Downloader with Search - Usage Example

This script demonstrates how to use the new search functionality.
Make sure you have:
1. YouTube Data API v3 key
2. Required packages installed: yt-dlp, requests
3. tkinter available (usually comes with Python)

Before running this example, set up your API key in the GUI.
"""

import sys
import os

def check_requirements():
    """Check if required packages are available"""
    try:
        import tkinter as tk
        print("✓ Tkinter is available")
    except ImportError:
        print("✗ Tkinter is not available. Please install python3-tk package.")
        return False
    
    try:
        import yt_dlp
        print("✓ yt-dlp is available")
    except ImportError:
        print("✗ yt-dlp is not available. Please install: pip install yt-dlp")
        return False
    
    try:
        import requests
        print("✓ requests is available")
    except ImportError:
        print("✗ requests is not available. Please install: pip install requests")
        return False
    
    return True

def main():
    """Main function to run the YouTube Downloader with Search"""
    print("YouTube Downloader with Search - Starting...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\nPlease install missing requirements and try again.")
        sys.exit(1)
    
    print("\nAll requirements satisfied!")
    print("\nStarting the application...")
    print("Don't forget to:")
    print("1. Set your YouTube Data API v3 key in the Search tab")
    print("2. Try searching with keywords like 'python tutorial'")
    print("3. Select language and learning level")
    print("4. Select videos and download them")
    
    # Import and run the application
    try:
        from yt_with_search import YouTubeDownloaderWithSearch
        import tkinter as tk
        
        root = tk.Tk()
        app = YouTubeDownloaderWithSearch(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()