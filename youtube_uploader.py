"""
유튜브 자동 업로드 스크립트
- YouTube Data API v3 사용
- 영상, 썸네일, 메타데이터 자동 업로드
- 예약 업로드 지원
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import json

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import pickle
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: YouTube API 라이브러리가 설치되지 않았습니다.")
    print("설치: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class YouTubeUploader:
    def __init__(self, credentials_file: str = "client_secrets.json"):
        """
        credentials_file: Google Cloud Console에서 다운로드한 OAuth 2.0 자격증명 파일
        """
        self.credentials_file = credentials_file
        self.token_file = "youtube_token.pickle"
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.youtube = None

        if YOUTUBE_API_AVAILABLE:
            self._authenticate()

    def _authenticate(self):
        """YouTube API 인증"""
        creds = None

        # 저장된 토큰 로드
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # 토큰이 없거나 만료된 경우
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    print(f"❌ {self.credentials_file} 파일이 없습니다.")
                    print("Google Cloud Console에서 OAuth 2.0 자격증명을 다운로드하세요.")
                    return

            # 토큰 저장
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        # YouTube API 클라이언트 생성
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube API 인증 완료")

    def upload_video(self, video_file: str, title: str, description: str,
                    tags: list = None, category_id: str = "22",
                    privacy_status: str = "public",
                    thumbnail_file: str = None,
                    publish_at: datetime = None) -> dict:
        """
        유튜브 영상 업로드

        Args:
            video_file: 업로드할 영상 파일 경로
            title: 영상 제목 (최대 100자)
            description: 영상 설명 (최대 5000자)
            tags: 태그 리스트 (최대 500자)
            category_id: 카테고리 ID (22=People & Blogs, 25=News & Politics)
            privacy_status: "public", "private", "unlisted"
            thumbnail_file: 썸네일 이미지 파일 경로
            publish_at: 예약 업로드 시간 (datetime 객체)

        Returns:
            업로드된 영상 정보
        """

        if not YOUTUBE_API_AVAILABLE or not self.youtube:
            return self._upload_mock(video_file, title, description)

        try:
            # 영상 메타데이터 설정
            body = {
                'snippet': {
                    'title': title[:100],  # 최대 100자
                    'description': description[:5000],  # 최대 5000자
                    'tags': tags[:] if tags else [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }

            # 예약 업로드 설정
            if publish_at and privacy_status == "private":
                body['status']['publishAt'] = publish_at.isoformat() + 'Z'
                body['status']['privacyStatus'] = 'private'

            # 영상 파일 업로드
            media = MediaFileUpload(
                video_file,
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )

            print(f"📤 '{title}' 업로드 시작...")

            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  업로드 진행: {progress}%")

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"✅ 영상 업로드 완료!")
            print(f"  영상 ID: {video_id}")
            print(f"  URL: {video_url}")

            # 썸네일 업로드
            if thumbnail_file and os.path.exists(thumbnail_file):
                self._upload_thumbnail(video_id, thumbnail_file)

            return {
                'status': 'success',
                'video_id': video_id,
                'video_url': video_url,
                'title': title,
                'privacy_status': privacy_status,
                'publish_at': publish_at.isoformat() if publish_at else None
            }

        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _upload_thumbnail(self, video_id: str, thumbnail_file: str):
        """썸네일 이미지 업로드"""
        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            print(f"  썸네일 업로드 완료: {thumbnail_file}")
        except Exception as e:
            print(f"  썸네일 업로드 실패: {e}")

    def _upload_mock(self, video_file: str, title: str, description: str) -> dict:
        """Mock 업로드 (테스트용)"""
        mock_video_id = f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        mock_url = f"https://www.youtube.com/watch?v={mock_video_id}"

        print(f"🎬 Mock 업로드 시뮬레이션")
        print(f"  파일: {video_file}")
        print(f"  제목: {title}")
        print(f"  설명: {description[:100]}...")
        print(f"  URL: {mock_url}")

        return {
            'status': 'success (mock)',
            'video_id': mock_video_id,
            'video_url': mock_url,
            'title': title
        }

    def update_video(self, video_id: str, title: str = None,
                    description: str = None, tags: list = None) -> dict:
        """업로드된 영상 정보 수정"""

        if not YOUTUBE_API_AVAILABLE or not self.youtube:
            return {'status': 'mock', 'message': 'API 사용 불가'}

        try:
            # 현재 영상 정보 가져오기
            video = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()

            if not video['items']:
                return {'status': 'error', 'message': 'Video not found'}

            snippet = video['items'][0]['snippet']

            # 업데이트할 정보 설정
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags

            # 업데이트 요청
            self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()

            print(f"✅ 영상 정보 업데이트 완료: {video_id}")
            return {'status': 'success', 'video_id': video_id}

        except Exception as e:
            print(f"❌ 업데이트 실패: {e}")
            return {'status': 'error', 'error': str(e)}

    def list_my_videos(self, max_results: int = 10) -> list:
        """내 채널의 최근 업로드 영상 목록 조회"""

        if not YOUTUBE_API_AVAILABLE or not self.youtube:
            return []

        try:
            # 내 채널 정보 가져오기
            channels = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()

            if not channels['items']:
                return []

            uploads_playlist_id = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # 업로드 영상 목록 가져오기
            playlist_items = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()

            videos = []
            for item in playlist_items['items']:
                videos.append({
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:100],
                    'published_at': item['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                })

            return videos

        except Exception as e:
            print(f"❌ 영상 목록 조회 실패: {e}")
            return []


# 사용 예시
if __name__ == "__main__":
    print("=" * 60)
    print("YouTube 자동 업로드 테스트")
    print("=" * 60)

    # Mock 모드로 테스트
    uploader = YouTubeUploader()

    # 업로드할 영상 정보
    video_info = {
        'video_file': 'output/videos/final_video.mp4',
        'title': '[속보] 삼성전자 반도체 50조 투자 결정! 주가 영향 분석',
        'description': '''
삼성전자가 차세대 반도체 생산을 위해 50조 원 규모의 대규모 투자를 결정했습니다.

이번 투자가 국내 경제와 주식시장에 미칠 영향을 전문가 의견과 함께 자세히 분석합니다.

📌 주요 내용:
- 투자 규모 및 분야
- 국내 경제 파급효과
- 삼성전자 주가 전망
- 관련 종목 영향 분석

출처: 네이버 뉴스

#삼성전자 #반도체투자 #주가전망 #경제뉴스 #시니어뉴스
        ''',
        'tags': ['삼성전자', '반도체', '투자', '주가', '경제뉴스', '시니어뉴스'],
        'category_id': '25',  # News & Politics
        'privacy_status': 'public',
        'thumbnail_file': 'output/thumbnails/thumbnail.jpg'
    }

    # 1. 즉시 업로드
    print("\n1️⃣ 즉시 업로드 테스트")
    result = uploader.upload_video(**video_info)
    print(f"\n결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 2. 예약 업로드 (내일 오후 6시)
    print("\n2️⃣ 예약 업로드 테스트")
    tomorrow_6pm = datetime.now() + timedelta(days=1)
    tomorrow_6pm = tomorrow_6pm.replace(hour=18, minute=0, second=0, microsecond=0)

    video_info['title'] = '[예약] 내일 공개될 중요한 뉴스'
    video_info['privacy_status'] = 'private'
    result = uploader.upload_video(**video_info, publish_at=tomorrow_6pm)
    print(f"\n결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 3. 내 영상 목록 조회
    print("\n3️⃣ 최근 업로드 영상 목록")
    videos = uploader.list_my_videos(max_results=5)
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   URL: {video['url']}")
        print(f"   업로드: {video['published_at']}")

    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료")
    print("=" * 60)

    print("\n📝 실제 사용을 위한 설정:")
    print("1. Google Cloud Console에서 YouTube Data API v3 활성화")
    print("2. OAuth 2.0 자격증명 생성 및 client_secrets.json 다운로드")
    print("3. pip install google-auth-oauthlib google-api-python-client")
    print("4. 위 스크립트 실행하여 인증")
