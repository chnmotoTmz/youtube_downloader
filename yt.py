import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import threading
from pathlib import Path
import re
import subprocess
import webbrowser
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

class YouTubeDownloaderWithSearch:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader with Search")
        self.root.geometry("800x600")
        
        # Load environment variables
        load_dotenv()
        
        # Download control
        self.current_process = None
        self.download_thread = None
        self.extract_thread = None
        self.search_thread = None
        self.is_extracting = False
        self.is_downloading = False
        self.is_searching = False
        
        # API settings
        self.api_key = os.getenv('YOUTUBE_API_KEY', '')
        
        # Check if .env file exists, if not create guidance
        self.check_env_file()
        
        # Search results storage
        self.search_results = []
        self.selected_videos = {}
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_download_tab()
        self.create_search_tab()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def check_env_file(self):
        """Check if .env file exists and guide user to create one"""
        env_path = Path('.env')
        env_example_path = Path('.env.example')
        
        if not env_path.exists() and env_example_path.exists():
            message = (
                "No .env file found!\n\n"
                "To use the search functionality, you need to set up your YouTube API key:\n\n"
                "1. Copy .env.example to .env\n"
                "2. Get your API key from:\n"
                "   https://console.cloud.google.com/apis/credentials\n"
                "3. Replace 'your_youtube_api_key_here' with your actual API key\n\n"
                "You can also enter the API key directly in the Search tab."
            )
            messagebox.showinfo("Setup Required", message)

    def create_download_tab(self):
        """Create the original download functionality tab"""
        self.download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.download_frame, text="Download")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.download_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        ttk.Label(main_frame, text="Enter YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output directory
        self.output_dir = str(Path.home() / "Downloads" / "YouTube_Audio")
        os.makedirs(self.output_dir, exist_ok=True)
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Button frame for output directory
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output directory path and open button
        self.dir_label = ttk.Label(dir_frame, text=self.output_dir, wraplength=500)
        self.dir_label.pack(side=tk.LEFT, padx=(0, 10))
        self.browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.select_output_dir)
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_dir_btn = ttk.Button(dir_frame, text="Open Folder", command=self.open_output_dir)
        self.open_dir_btn.pack(side=tk.RIGHT)
        
        # Download format selection
        ttk.Label(main_frame, text="Download Format:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="mp3")
        self.mp3_radio = ttk.Radiobutton(main_frame, text="MP3 (Audio)", variable=self.format_var, value="mp3")
        self.mp3_radio.grid(row=5, column=0, sticky=tk.W, padx=10)
        self.mp4_radio = ttk.Radiobutton(main_frame, text="MP4 (Video)", variable=self.format_var, value="mp4")
        self.mp4_radio.grid(row=5, column=1, sticky=tk.W)
        
        # Button frame for download controls
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Download and Cancel buttons
        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.extract_list_btn = ttk.Button(button_frame, text="Extract List URLs", command=self.start_extract_playlist_urls)
        self.extract_list_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=650, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Download list
        self.download_list = tk.Text(main_frame, height=12, width=70)
        self.download_list.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.download_list.yview)
        scrollbar.grid(row=9, column=2, sticky=(tk.N, tk.S))
        self.download_list.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)

    def create_search_tab(self):
        """Create the new search functionality tab"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search")
        
        # Main frame with padding
        main_frame = ttk.Frame(self.search_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key section
        api_frame = ttk.LabelFrame(main_frame, text="YouTube Data API Settings", padding="5")
        api_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.api_key_var = tk.StringVar(value=self.api_key)
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(api_frame, text="Set API Key", command=self.set_api_key).grid(row=0, column=2, padx=5)
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="5")
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Search keyword
        ttk.Label(search_frame, text="Search Keyword:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.search_keyword_var = tk.StringVar()
        self.search_keyword_entry = ttk.Entry(search_frame, textvariable=self.search_keyword_var, width=40)
        self.search_keyword_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Language selection
        ttk.Label(search_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.language_var = tk.StringVar(value="ja")
        language_frame = ttk.Frame(search_frame)
        language_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(language_frame, text="Japanese", variable=self.language_var, value="ja").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(language_frame, text="Chinese", variable=self.language_var, value="zh").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(language_frame, text="Korean", variable=self.language_var, value="ko").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(language_frame, text="English", variable=self.language_var, value="en").pack(side=tk.LEFT, padx=5)
        
        # Learning level
        ttk.Label(search_frame, text="Learning Level:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.level_var = tk.StringVar(value="beginner")
        level_frame = ttk.Frame(search_frame)
        level_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(level_frame, text="Beginner", variable=self.level_var, value="beginner").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(level_frame, text="Intermediate", variable=self.level_var, value="intermediate").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(level_frame, text="Advanced", variable=self.level_var, value="advanced").pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn_frame = ttk.Frame(search_frame)
        search_btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.search_btn = ttk.Button(search_btn_frame, text="Search Videos", command=self.start_search)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.search_cancel_btn = ttk.Button(search_btn_frame, text="Cancel Search", command=self.cancel_search, state=tk.DISABLED)
        self.search_cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Search results section
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="5")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Results treeview
        columns = ("Select", "Title", "Channel", "Duration", "Views", "Published")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.results_tree.heading("Select", text="Select")
        self.results_tree.heading("Title", text="Title")
        self.results_tree.heading("Channel", text="Channel")
        self.results_tree.heading("Duration", text="Duration")
        self.results_tree.heading("Views", text="Views")
        self.results_tree.heading("Published", text="Published")
        
        self.results_tree.column("Select", width=50, anchor=tk.CENTER)
        self.results_tree.column("Title", width=300)
        self.results_tree.column("Channel", width=150)
        self.results_tree.column("Duration", width=80, anchor=tk.CENTER)
        self.results_tree.column("Views", width=100, anchor=tk.CENTER)
        self.results_tree.column("Published", width=100, anchor=tk.CENTER)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results scrollbar
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        # Bind double-click to toggle selection
        self.results_tree.bind("<Double-1>", self.toggle_video_selection)
        self.results_tree.bind("<Button-1>", self.on_treeview_click)
        
        # Download selected section
        download_selected_frame = ttk.Frame(main_frame)
        download_selected_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(download_selected_frame, text="Select All", command=self.select_all_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(download_selected_frame, text="Deselect All", command=self.deselect_all_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(download_selected_frame, text="Download Selected", command=self.download_selected_videos).pack(side=tk.LEFT, padx=5)
        
        # Status for search
        self.search_status_var = tk.StringVar(value="Ready to search")
        self.search_status_label = ttk.Label(main_frame, textvariable=self.search_status_var)
        self.search_status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    def set_api_key(self):
        """Set the YouTube Data API key"""
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.api_key = api_key
            messagebox.showinfo("Success", "API Key set successfully!")
        else:
            messagebox.showerror("Error", "Please enter a valid API key")

    def start_search(self):
        """Start searching for videos"""
        if not self.api_key:
            messagebox.showerror("Error", "Please set your YouTube Data API key first")
            return
        
        keyword = self.search_keyword_var.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Please enter a search keyword")
            return
        
        self.is_searching = True
        self.search_btn.config(state=tk.DISABLED)
        self.search_cancel_btn.config(state=tk.NORMAL)
        self.search_status_var.set("Searching...")
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.search_results = []
        self.selected_videos = {}
        
        self.search_thread = threading.Thread(target=self.search_videos, args=(keyword,), daemon=True)
        self.search_thread.start()

    def search_videos(self, keyword):
        """Search for videos using YouTube Data API"""
        try:
            language = self.language_var.get()
            level = self.level_var.get()
            
            # Modify search query based on language and level
            search_query = f"{keyword} {level} lesson"
            if language == "ja":
                search_query += " 日本語"
            elif language == "zh":
                search_query += " 中文"
            elif language == "ko":
                search_query += " 한국어"
            
            # YouTube Data API search
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': 25,
                'key': self.api_key,
                'relevanceLanguage': language
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not self.is_searching:
                return
            
            # Get video details (duration, view count, etc.)
            video_ids = [item['id']['videoId'] for item in data.get('items', [])]
            if video_ids:
                details_url = "https://www.googleapis.com/youtube/v3/videos"
                details_params = {
                    'part': 'contentDetails,statistics',
                    'id': ','.join(video_ids),
                    'key': self.api_key
                }
                
                details_response = requests.get(details_url, params=details_params)
                details_response.raise_for_status()
                details_data = details_response.json()
                
                # Create a mapping of video details
                video_details = {item['id']: item for item in details_data.get('items', [])}
                
                # Process results
                for item in data.get('items', []):
                    if not self.is_searching:
                        return
                    
                    video_id = item['id']['videoId']
                    snippet = item['snippet']
                    details = video_details.get(video_id, {})
                    
                    video_info = {
                        'id': video_id,
                        'title': snippet['title'],
                        'channel': snippet['channelTitle'],
                        'published': snippet['publishedAt'][:10],
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'duration': self.parse_duration(details.get('contentDetails', {}).get('duration', 'PT0S')),
                        'views': int(details.get('statistics', {}).get('viewCount', 0))
                    }
                    
                    self.search_results.append(video_info)
                    
                    # Add to treeview
                    self.root.after(0, self.add_result_to_tree, video_info)
            
            self.root.after(0, self.search_status_var.set, f"Found {len(self.search_results)} videos")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.root.after(0, self.search_status_var.set, error_msg)
            self.root.after(0, messagebox.showerror, "Network Error", error_msg)
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            self.root.after(0, self.search_status_var.set, error_msg)
            self.root.after(0, messagebox.showerror, "Search Error", error_msg)
        finally:
            if self.is_searching:
                self.is_searching = False
                self.root.after(0, self.search_btn.config, {'state': tk.NORMAL})
                self.root.after(0, self.search_cancel_btn.config, {'state': tk.DISABLED})

    def parse_duration(self, duration_str):
        """Parse ISO 8601 duration to readable format"""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if match:
            hours, minutes, seconds = match.groups()
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            seconds = int(seconds) if seconds else 0
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        return "0:00"

    def add_result_to_tree(self, video_info):
        """Add search result to the treeview"""
        views_str = f"{video_info['views']:,}" if video_info['views'] > 0 else "N/A"
        
        item_id = self.results_tree.insert("", "end", values=(
            "☐",  # Checkbox symbol
            video_info['title'][:50] + "..." if len(video_info['title']) > 50 else video_info['title'],
            video_info['channel'][:20] + "..." if len(video_info['channel']) > 20 else video_info['channel'],
            video_info['duration'],
            views_str,
            video_info['published']
        ))
        
        # Store video info with item id
        self.selected_videos[item_id] = {'selected': False, 'info': video_info}

    def on_treeview_click(self, event):
        """Handle treeview click events"""
        region = self.results_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.results_tree.identify_column(event.x, event.y)
            if column == "#1":  # Select column
                self.toggle_video_selection(event)

    def toggle_video_selection(self, event):
        """Toggle video selection"""
        item = self.results_tree.selection()[0] if self.results_tree.selection() else None
        if item and item in self.selected_videos:
            current_selection = self.selected_videos[item]['selected']
            new_selection = not current_selection
            self.selected_videos[item]['selected'] = new_selection
            
            # Update checkbox display
            checkbox_symbol = "☑" if new_selection else "☐"
            values = list(self.results_tree.item(item, "values"))
            values[0] = checkbox_symbol
            self.results_tree.item(item, values=values)

    def select_all_videos(self):
        """Select all videos in search results"""
        for item_id in self.selected_videos:
            self.selected_videos[item_id]['selected'] = True
            values = list(self.results_tree.item(item_id, "values"))
            values[0] = "☑"
            self.results_tree.item(item_id, values=values)

    def deselect_all_videos(self):
        """Deselect all videos in search results"""
        for item_id in self.selected_videos:
            self.selected_videos[item_id]['selected'] = False
            values = list(self.results_tree.item(item_id, "values"))
            values[0] = "☐"
            self.results_tree.item(item_id, values=values)

    def download_selected_videos(self):
        """Download all selected videos"""
        selected_urls = []
        for item_id, video_data in self.selected_videos.items():
            if video_data['selected']:
                selected_urls.append(video_data['info']['url'])
        
        if not selected_urls:
            messagebox.showwarning("Warning", "Please select at least one video to download")
            return
        
        # Switch to download tab
        self.notebook.select(0)
        
        # Start batch download
        self.start_batch_download(selected_urls)

    def start_batch_download(self, urls):
        """Start downloading multiple videos"""
        if self.is_downloading:
            messagebox.showwarning("Warning", "A download is already in progress")
            return
        
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.extract_list_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.mp3_radio.config(state=tk.DISABLED)
        self.mp4_radio.config(state=tk.DISABLED)
        
        self.download_thread = threading.Thread(target=self.batch_download_videos, args=(urls,), daemon=True)
        self.download_thread.start()

    def batch_download_videos(self, urls):
        """Download multiple videos"""
        total_videos = len(urls)
        for i, url in enumerate(urls, 1):
            if not self.is_downloading:
                break
            
            self.root.after(0, self.update_status, f"Downloading video {i}/{total_videos}")
            self.root.after(0, self.add_to_download_list, f"Starting download {i}/{total_videos}: {url}")
            
            try:
                self.download_single_video(url)
            except Exception as e:
                error_msg = f"Error downloading {url}: {str(e)}"
                self.root.after(0, self.add_to_download_list, error_msg)
        
        if self.is_downloading:
            self.root.after(0, self.update_status, "Batch download completed")
            self.root.after(0, self.add_to_download_list, f"✓ Batch download completed: {total_videos} videos")
        
        # Reset UI
        self.is_downloading = False
        self.root.after(0, self.download_btn.config, {'state': tk.NORMAL})
        self.root.after(0, self.extract_list_btn.config, {'state': tk.NORMAL})
        self.root.after(0, self.cancel_btn.config, {'state': tk.DISABLED})
        self.root.after(0, self.mp3_radio.config, {'state': tk.NORMAL})
        self.root.after(0, self.mp4_radio.config, {'state': tk.NORMAL})
        self.root.after(0, self.update_progress, 0)
        self.root.after(0, self.update_status, "Ready")

    def download_single_video(self, url):
        """Download a single video (used for batch downloads)"""
        class MyLogger:
            def debug(self, msg):
                pass
            def warning(self, msg):
                pass
            def error(self, msg):
                print(f'Error: {msg}')

        def my_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = d.get('_percent_str', '0%')
                    percent = re.sub(r'[^\d.]', '', percent)
                    # Update progress but don't overwhelm the UI during batch downloads
                except (ValueError, TypeError):
                    pass
            elif d['status'] == 'finished':
                pass

        selected_format = self.format_var.get()
        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [my_hook],
            'logger': MyLogger(),
            'noplaylist': True,
        }

        if selected_format == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            output_ext = 'mp3'
        elif selected_format == 'mp4':
            ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best'
            output_ext = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not self.is_downloading:
                return
            title = info.get('title', 'Unknown Title')
            self.root.after(0, self.add_to_download_list, f"✓ Downloaded: {title}.{output_ext}")

    def cancel_search(self):
        """Cancel the current search"""
        self.is_searching = False
        self.search_btn.config(state=tk.NORMAL)
        self.search_cancel_btn.config(state=tk.DISABLED)
        self.search_status_var.set("Search canceled")

    # Original download functionality methods (unchanged)
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def update_progress(self, progress):
        self.progress_var.set(progress)
        self.root.update_idletasks()

    def add_to_download_list(self, message):
        self.download_list.insert(tk.END, message + "\n")
        self.download_list.see(tk.END)
        self.root.update_idletasks()

    def open_output_dir(self):
        """Open the output directory in file explorer"""
        if os.path.exists(self.output_dir):
            if os.name == 'nt':  # Windows
                os.startfile(self.output_dir)
            else:  # macOS and Linux
                webbrowser.open('file://' + self.output_dir)

    def cancel_download(self):
        """Cancel the current download"""
        if self.is_downloading:
            self.is_downloading = False
            self.update_status("Canceling download...")
            self.add_to_download_list("Download canceled by user")
            
            # Reset UI
            self.download_btn.config(state=tk.NORMAL)
            self.extract_list_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.mp3_radio.config(state=tk.NORMAL)
            self.mp4_radio.config(state=tk.NORMAL)
            self.update_progress(0)
            self.update_status("Ready")

    def on_closing(self):
        """Handle window closing"""
        if self.is_downloading or self.is_searching:
            if messagebox.askokcancel("Quit", "An operation is in progress. Do you want to cancel and quit?"):
                self.is_downloading = False
                self.is_searching = False
                self.root.destroy()
        elif self.is_extracting:
            if messagebox.askokcancel("Quit", "URL extraction is in progress. Do you want to quit?"):
                self.is_extracting = False
                self.root.destroy()
        else:
            self.root.destroy()

    def sanitize_filename(self, name):
        """Remove characters that are invalid for filenames."""
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    def download_video(self, url):
        try:
            class MyLogger:
                def debug(self, msg):
                    pass
                def warning(self, msg):
                    pass
                def error(self, msg):
                    print(f'Error: {msg}')

            def my_hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = d.get('_percent_str', '0%')
                        percent = re.sub(r'[^\d.]', '', percent)
                        self.update_progress(float(percent))
                        self.update_status(f"Downloading: {percent}%")
                        self.root.after(0, self.update_status, f"Downloading: {percent}%")
                    except (ValueError, TypeError):
                        pass
                elif d['status'] == 'finished':
                    self.update_status("Download finished, converting...")
                    self.root.after(0, self.update_status, "Download finished, converting...")
                    self.update_progress(100)

            selected_format = self.format_var.get()
            ydl_opts = {
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [my_hook],
                'logger': MyLogger(),
                'noplaylist': True,
            }

            if selected_format == 'mp3':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                output_ext = 'mp3'
            elif selected_format == 'mp4':
                ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best'
                output_ext = 'mp4'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_status("Starting download...")
                self.root.after(0, self.update_status, "Starting download...")
                info = ydl.extract_info(url, download=True)
                if not self.is_downloading:
                    return
                self.add_to_download_list(f"✓ Downloaded: {info['title']}.{output_ext}")
                
                actual_ext = info.get('ext', output_ext)
                title = info.get('title', 'Unknown Title')
                self.root.after(0, self.add_to_download_list, f"✓ Downloaded: {title}.{actual_ext}")

        except Exception as e:
            if self.is_downloading:
                self.update_status(f"Error: {str(e)}")
                self.add_to_download_list(f"Error downloading {url}: {str(e)}")
                error_msg = f"Error: {str(e)}"
                self.root.after(0, self.update_status, error_msg)
                self.root.after(0, self.add_to_download_list, f"Error downloading {url}: {str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.config(state=tk.NORMAL)
            self.extract_list_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.mp3_radio.config(state=tk.NORMAL)
            self.mp4_radio.config(state=tk.NORMAL)
            self.update_progress(0)
            self.update_status("Ready")

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.extract_list_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.mp3_radio.config(state=tk.DISABLED)
        self.mp4_radio.config(state=tk.DISABLED)
        self.download_thread = threading.Thread(target=self.download_video, args=(url,), daemon=True)
        self.download_thread.start()

    def extract_playlist_urls(self, url):
        try:
            self.root.after(0, self.update_status, "Extracting playlist info...")
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if not self.is_extracting:
                return

            if 'entries' not in info or not info['entries']:
                self.root.after(0, self.update_status, "Error: No video entries found in the playlist.")
                self.root.after(0, self.add_to_download_list, f"Error: Could not find videos in playlist {url}")
                return

            playlist_title = self.sanitize_filename(info.get('title', 'playlist'))
            output_filename = os.path.join(self.output_dir, f"{playlist_title}_urls.txt")

            urls = [entry.get('url') for entry in info['entries'] if entry and entry.get('url')]

            if not urls:
                self.root.after(0, self.update_status, "Error: Could not extract video URLs.")
                self.root.after(0, self.add_to_download_list, f"Error: Failed to extract URLs from playlist {url}")
                return

            with open(output_filename, 'w', encoding='utf-8') as f:
                for video_url in urls:
                    f.write(video_url + '\n')

            success_msg = f"✓ Extracted {len(urls)} URLs to {output_filename}"
            self.root.after(0, self.add_to_download_list, success_msg)
            self.root.after(0, self.update_status, "Playlist URL extraction complete.")

        except Exception as e:
            error_msg = f"Error extracting playlist: {str(e)}"
            self.root.after(0, self.update_status, error_msg)
            self.root.after(0, self.add_to_download_list, f"Error extracting playlist {url}: {str(e)}")
        finally:
            if self.is_extracting:
                self.is_extracting = False
                self.root.after(0, self.download_btn.config, {'state': tk.NORMAL})
                self.root.after(0, self.extract_list_btn.config, {'state': tk.NORMAL})
                self.root.after(0, self.mp3_radio.config, {'state': tk.NORMAL})
                self.root.after(0, self.mp4_radio.config, {'state': tk.NORMAL})
                self.root.after(0, self.update_status, "Ready")

    def start_extract_playlist_urls(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        self.is_extracting = True
        self.download_btn.config(state=tk.DISABLED)
        self.extract_list_btn.config(state=tk.DISABLED)
        self.mp3_radio.config(state=tk.DISABLED)
        self.mp4_radio.config(state=tk.DISABLED)
        self.extract_thread = threading.Thread(target=self.extract_playlist_urls, args=(url,), daemon=True)
        self.extract_thread.start()

    def select_output_dir(self):
        """Open directory selection dialog and update output path"""
        selected_dir = filedialog.askdirectory(initialdir=self.output_dir)
        if selected_dir:
            self.output_dir = selected_dir
            self.dir_label.config(text=self.output_dir)
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderWithSearch(root)
    root.mainloop()
