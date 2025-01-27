# YouTube MP3 Downloader

A simple GUI application that downloads YouTube videos and converts them to MP3 format. Built with Python and Tkinter.

## Features

- Easy-to-use graphical interface
- Downloads YouTube videos and automatically converts to MP3
- Shows download progress with progress bar
- Displays download history
- Allows canceling ongoing downloads
- Quick access to download folder
- Supports high-quality audio extraction (192kbps)
- Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- Python 3.6 or higher
- ffmpeg
- Required Python packages:
  - yt-dlp
  - tkinter (usually comes with Python)

## Installation

1. First, ensure you have Python 3.6+ installed on your system.

2. Install ffmpeg:
   
   **Windows (using Chocolatey):**
   ```bash
   choco install ffmpeg
   ```
   
   **macOS (using Homebrew):**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install ffmpeg
   ```

3. Install required Python packages:
   ```bash
   pip install yt-dlp
   ```

4. Download `yt.py` and save it to your preferred location.

## Usage

1. Run the application:
   ```bash
   python yt.py
   ```

2. The application window will open with the following features:
   - URL input field
   - Download button
   - Cancel button
   - Progress bar
   - Download history
   - Open Folder button

3. To download a video:
   - Paste a YouTube URL into the input field
   - Click "Download"
   - Wait for the download and conversion to complete
   - The MP3 file will be saved in your Downloads/YouTube_Audio folder

4. Additional functions:
   - Click "Cancel" to stop an ongoing download
   - Click "Open Folder" to view your downloaded files
   - The download history shows all completed and failed downloads

## Default Save Location

Downloaded MP3 files are saved to:
- Windows: `C:\Users\<username>\Downloads\YouTube_Audio`
- macOS/Linux: `/home/<username>/Downloads/YouTube_Audio`

## Troubleshooting

1. **FFmpeg not found error:**
   - Ensure ffmpeg is installed correctly
   - Make sure ffmpeg is in your system PATH
   - Try reinstalling ffmpeg

2. **Download fails:**
   - Check your internet connection
   - Verify the YouTube URL is valid
   - Ensure you have write permissions in the download directory

3. **Conversion fails:**
   - Check if ffmpeg is installed correctly
   - Ensure enough disk space is available
   - Check the download directory permissions

## Notes

- The application requires an active internet connection
- Download speed depends on your internet connection
- Some videos might not be available for download due to restrictions
- The application automatically creates the YouTube_Audio folder if it doesn't exist

## License

This project is open source and available under the MIT License.

## Credits

This application uses the following open-source packages:
- yt-dlp
- ffmpeg
- Python Tkinter