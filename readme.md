# YouTube ダウンローダー

YouTubeの動画をMP3またはMP4形式でダウンロードできるGUIアプリケーションです。PythonとTkinterで作成されています。

## 主な機能

- 使いやすいグラフィカルインターフェース
- YouTube動画のダウンロードとMP3/MP4形式の選択保存
- 保存先フォルダを自由に選択可能（「Browse...」ボタン）
- プレイリストURLを入力して、含まれる動画URL一覧をテキストファイルに出力
- プログレスバーでダウンロードの進捗を表示
- ダウンロード履歴の表示
- 進行中のダウンロードのキャンセル機能
- ダウンロードフォルダへの簡単アクセス
- 高品質音声抽出（192kbps）対応
- クロスプラットフォーム対応（Windows、macOS、Linux）

## 必要な環境

- Python 3.6以上
- ffmpeg
- 必要なPythonパッケージ：
  - yt-dlp
  - tkinter（通常はPythonに同梱）

## インストール手順

1. Python 3.6以上がインストールされていることを確認してください。
2. ffmpegのインストール：
   - Windows（Chocolatey）：
     ```bash
     choco install ffmpeg
     ```
   - macOS（Homebrew）：
     ```bash
     brew install ffmpeg
     ```
   - Linux（Ubuntu/Debian）：
     ```bash
     sudo apt-get install ffmpeg
     ```
3. 必要なPythonパッケージのインストール：
   ```bash
   pip install yt-dlp
   ```
4. `yt.py`をダウンロードし、任意の場所に保存してください。

## 使い方

1. アプリケーションの起動：
   ```bash
   python yt.py
   ```
2. アプリケーションウィンドウの主な機能：
   - URL入力フィールド
   - 保存先フォルダ表示と「Browse...」ボタン（保存先を自由に選択可能）
   - ダウンロード形式選択（MP3/MP4ラジオボタン）
   - ダウンロードボタン
   - キャンセルボタン
   - プログレスバー
   - ダウンロード履歴
   - フォルダを開くボタン
   - 「Extract List URLs」ボタン（プレイリストURL抽出）

3. 動画のダウンロード方法：
   - YouTubeの動画またはプレイリストのURLを入力フィールドに貼り付け
   - 保存先フォルダを必要に応じて「Browse...」で変更
   - ダウンロード形式（MP3またはMP4）を選択
   - 「Download」をクリック
   - ダウンロードと変換が完了するまで待機
   - 選択した保存先フォルダにファイルが保存されます

4. プレイリストURLの動画一覧抽出：
   - プレイリストのURLを入力
   - 「Extract List URLs」ボタンをクリック
   - 保存先フォルダに「[プレイリスト名]_urls.txt」として動画URL一覧が保存されます

5. その他の機能：
   - 「Cancel」で進行中のダウンロードを中止
   - 「Open Folder」で保存先フォルダを開く
   - ダウンロード履歴で完了・失敗したダウンロードを確認可能

## 保存先フォルダ

ダウンロードしたファイルは、デフォルトでは以下の場所に保存されますが、「Browse...」ボタンで任意のフォルダに変更できます：
- Windows：`C:\Users\<ユーザー名>\Downloads\YouTube_Audio`
- macOS/Linux：`/home/<ユーザー名>/Downloads/YouTube_Audio`

## トラブルシューティング

1. **FFmpegが見つからないエラー：**
   - ffmpegが正しくインストールされているか確認
   - ffmpegがシステムPATHに含まれているか確認
   - ffmpegの再インストールを試してみる
2. **ダウンロードが失敗する：**
   - インターネット接続を確認
   - YouTube URLが有効か確認
   - ダウンロードディレクトリの書き込み権限を確認
3. **変換が失敗する：**
   - ffmpegが正しくインストールされているか確認
   - 十分なディスク容量があるか確認
   - ダウンロードディレクトリのアクセス権限を確認

## 注意事項

- インターネット接続が必要です
- ダウンロード速度はインターネット接続速度に依存します
- 制限により一部の動画はダウンロードできない場合があります
- 保存先フォルダは存在しない場合、自動的に作成されます

## ライセンス

このプロジェクトはMITライセンスのもとでオープンソースとして公開されています。

## クレジット

このアプリケーションは以下のオープンソースパッケージを使用しています：
- yt-dlp
- ffmpeg
- Python Tkinter

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