#!/usr/bin/env python3
"""
YouTube Data API v3 検索機能テスト
"""

import requests
import json

def test_youtube_search():
    """YouTube Data API v3の検索機能をテスト"""
    api_key = "AIzaSyBkkKQsKrU1aGlTw-2c5H61VgFqHX0TRUg"
    
    # テスト検索パラメータ
    keyword = "python tutorial"
    language = "en"
    level = "beginner"
    
    # 検索クエリの構築
    search_query = f"{keyword} {level} lesson"
    
    print(f"検索中: {search_query}")
    print(f"言語: {language}")
    print("=" * 50)
    
    try:
        # YouTube Data API検索
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'maxResults': 5,  # テスト用に5件に制限
            'key': api_key,
            'relevanceLanguage': language
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"検索結果: {len(data.get('items', []))} 件見つかりました\n")
        
        # 動画IDを取得
        video_ids = [item['id']['videoId'] for item in data.get('items', [])]
        
        if video_ids:
            # 動画詳細情報を取得
            details_url = "https://www.googleapis.com/youtube/v3/videos"
            details_params = {
                'part': 'contentDetails,statistics',
                'id': ','.join(video_ids),
                'key': api_key
            }
            
            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details_data = details_response.json()
            
            # 詳細情報をマップ
            video_details = {item['id']: item for item in details_data.get('items', [])}
            
            # 結果を表示
            for i, item in enumerate(data.get('items', []), 1):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                details = video_details.get(video_id, {})
                
                print(f"{i}. タイトル: {snippet['title']}")
                print(f"   チャンネル: {snippet['channelTitle']}")
                print(f"   投稿日: {snippet['publishedAt'][:10]}")
                print(f"   URL: https://www.youtube.com/watch?v={video_id}")
                
                # 再生時間の解析
                duration = details.get('contentDetails', {}).get('duration', 'PT0S')
                duration_readable = parse_duration(duration)
                print(f"   再生時間: {duration_readable}")
                
                # 視聴回数
                views = int(details.get('statistics', {}).get('viewCount', 0))
                print(f"   視聴回数: {views:,}")
                print()
        
        print("✅ API検索テスト成功！")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ネットワークエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def parse_duration(duration_str):
    """ISO 8601時間形式を読みやすい形式に変換"""
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

if __name__ == "__main__":
    print("YouTube Data API v3 検索機能テスト")
    print("=" * 50)
    test_youtube_search()