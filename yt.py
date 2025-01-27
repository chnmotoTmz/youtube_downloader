import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
import os
import threading
from pathlib import Path
import re
import subprocess
import webbrowser

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("600x400")
        
        # Download control
        self.current_process = None
        self.download_thread = None
        self.is_downloading = False

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL input
        ttk.Label(self.main_frame, text="Enter YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Output directory
        self.output_dir = str(Path.home() / "Downloads" / "YouTube_Audio")
        os.makedirs(self.output_dir, exist_ok=True)
        ttk.Label(self.main_frame, text=f"Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Button frame for output directory
        self.dir_frame = ttk.Frame(self.main_frame)
        self.dir_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output directory path and open button
        self.dir_label = ttk.Label(self.dir_frame, text=self.output_dir)
        self.dir_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_dir_btn = ttk.Button(self.dir_frame, text="Open Folder", command=self.open_output_dir)
        self.open_dir_btn.pack(side=tk.RIGHT)

        # Button frame for download controls
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Download and Cancel buttons
        self.download_btn = ttk.Button(self.button_frame, text="Download", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(self.button_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Download list
        self.download_list = tk.Text(self.main_frame, height=10, width=50)
        self.download_list.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.download_list.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.download_list.configure(yscrollcommand=scrollbar.set)

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
            self.cancel_btn.config(state=tk.DISABLED)
            self.update_progress(0)
            self.update_status("Ready")

    def on_closing(self):
        """Handle window closing"""
        if self.is_downloading:
            if messagebox.askokcancel("Quit", "A download is in progress. Do you want to cancel and quit?"):
                self.cancel_download()
                self.root.destroy()
        else:
            self.root.destroy()

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
                    except (ValueError, TypeError):
                        pass
                elif d['status'] == 'finished':
                    self.update_status("Download finished, converting...")
                    self.update_progress(100)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [my_hook],
                'logger': MyLogger(),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_status("Starting download...")
                info = ydl.extract_info(url, download=True)
                if not self.is_downloading:  # Check if canceled
                    return
                self.add_to_download_list(f"✓ Downloaded and converted: {info['title']}.mp3")
                
        except Exception as e:
            if self.is_downloading:  # Only show error if not canceled
                self.update_status(f"Error: {str(e)}")
                self.add_to_download_list(f"Error downloading {url}: {str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.update_progress(0)
            self.update_status("Ready")

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.download_thread = threading.Thread(target=self.download_video, args=(url,), daemon=True)
        self.download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()