# 🎬 뉴스 기반 유튜브 자동화 시스템

뉴스 기사를 자동으로 수집하고, AI로 대본을 작성하며, TTS로 음성을 생성하여 유튜브 영상을 자동으로 제작하는 완전 자동화 시스템입니다.

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [주요 기능](#주요-기능)
3. [설치 방법](#설치-방법)
4. [사용 방법](#사용-방법)
5. [API 설정](#api-설정)
6. [파일 구조](#파일-구조)

---

## 🎯 시스템 개요

이 시스템은 6단계 워크플로우로 구성되어 있습니다:

```
1. 뉴스 수집 → 2. AI 대본 생성 → 3. 썸네일 제목 생성
→ 4. TTS 음성 생성 → 5. 영상 편집 → 6. 유튜브 업로드
```

### 🎥 예상 소요 시간
- **전체 워크플로우**: 영상 1개당 약 5~10분
- **하루 3개 영상 제작**: 약 30분~1시간

### 💰 예상 비용 (월 90개 영상 기준)
- OpenAI GPT-4: 약 $20~30
- ElevenLabs TTS: 약 $22 (Professional Plan)
- YouTube API: 무료
- **총 예상 비용**: 약 $40~50/월

---

## 🚀 주요 기능

### 1. 뉴스 수집 (`news_collector.py`)
- ✅ Google News RSS 자동 수집 (API 키 불필요)
- ✅ 네이버 뉴스 API 지원
- ✅ 키워드 기반 필터링
- ✅ 관련성 점수로 자동 정렬

### 2. AI 대본 생성 (`ai_script_generator.py`)
- ✅ OpenAI GPT-4 / Google Gemini / Anthropic Claude 지원
- ✅ 시니어층(40~60대) 타겟 톤 자동 적용
- ✅ 8~10분 분량 대본 자동 생성
- ✅ 도입부, 본문, 마무리 구조화

### 3. 썸네일 제목 생성
- ✅ CTR 높은 제목 10개 자동 생성
- ✅ 다양한 스타일: 질문형, 숫자형, 충격형, 반전형

### 4. TTS 음성 생성 (`tts_generator.py`)
- ✅ ElevenLabs (최고 품질, 추천)
- ✅ Google Cloud TTS
- ✅ Azure TTS
- ✅ 자연스러운 한국어 음성

### 5. 영상 편집
- ✅ Vrew 자동 자막 생성 연동
- ✅ FFmpeg 기반 자동 편집 (개발 예정)

### 6. 유튜브 업로드 (`youtube_uploader.py`)
- ✅ YouTube Data API v3 연동
- ✅ 썸네일, 제목, 설명, 태그 자동 입력
- ✅ 예약 업로드 지원

---

## 💻 설치 방법

### 1. Python 설치
Python 3.8 이상 필요합니다.

```bash
# Python 버전 확인
python --version
```

### 2. 의존성 패키지 설치

```bash
# 필수 패키지
pip install requests beautifulsoup4 feedparser

# AI 서비스 (선택)
pip install openai google-generativeai anthropic

# TTS 서비스 (선택)
pip install google-cloud-texttospeech azure-cognitiveservices-speech

# YouTube API
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 오디오 처리 (선택)
pip install pydub
```

또는 `requirements.txt` 사용:

```bash
pip install -r requirements.txt
```

### 3. 프로젝트 클론

```bash
git clone <repository-url>
cd news
```

---

## 📖 사용 방법

### 방법 1: 웹 대시보드 사용 (추천 - 초보자용)

1. `dashboard.html` 파일을 브라우저로 열기
2. 각 단계별 버튼 클릭으로 진행
3. 시각적으로 진행상황 확인

```bash
# 브라우저에서 열기
start dashboard.html  # Windows
open dashboard.html   # Mac
xdg-open dashboard.html  # Linux
```

### 방법 2: Python 통합 스크립트 실행

```bash
# 전체 워크플로우 자동 실행
python main_workflow.py
```

### 방법 3: 개별 모듈 실행

```bash
# 1. 뉴스 수집
python news_collector.py

# 2. AI 대본 생성
python ai_script_generator.py

# 3. TTS 음성 생성
python tts_generator.py

# 4. 유튜브 업로드
python youtube_uploader.py
```

---

## 🔑 API 설정

### 1. OpenAI GPT API

1. https://platform.openai.com 에서 API 키 발급
2. `main_workflow.py`의 `config`에 추가:

```python
config = {
    'ai_service': 'openai',
    'ai_api_key': 'sk-xxxxxxxxxxxxxxxx'
}
```

### 2. ElevenLabs TTS API

1. https://elevenlabs.io 에서 계정 생성
2. API 키 발급:

```python
config = {
    'tts_service': 'elevenlabs',
    'tts_api_key': 'your_elevenlabs_api_key'
}
```

### 3. YouTube Data API v3

#### 단계별 설정:

1. **Google Cloud Console** 접속
   - https://console.cloud.google.com

2. **새 프로젝트 생성**
   - 프로젝트 이름: "YouTube Automation"

3. **YouTube Data API v3 활성화**
   - API 및 서비스 → 라이브러리
   - "YouTube Data API v3" 검색 → 사용 설정

4. **OAuth 2.0 자격증명 생성**
   - 사용자 인증 정보 → 사용자 인증 정보 만들기
   - OAuth 클라이언트 ID → 데스크톱 앱
   - `client_secrets.json` 다운로드

5. **파일 배치**
   ```
   news/
   ├── client_secrets.json  ← 여기에 배치
   ├── main_workflow.py
   └── ...
   ```

6. **첫 실행 시 인증**
   ```bash
   python youtube_uploader.py
   ```
   - 브라우저가 자동으로 열림
   - Google 계정 로그인 및 권한 승인
   - `youtube_token.pickle` 파일 자동 생성

### 4. 네이버 뉴스 API (선택)

1. https://developers.naver.com/apps/#/register
2. 애플리케이션 등록 → 검색 API 선택
3. `news_collector.py`에 키 입력:

```python
headers = {
    "X-Naver-Client-Id": "YOUR_CLIENT_ID",
    "X-Naver-Client-Secret": "YOUR_CLIENT_SECRET"
}
```

---

## 📁 파일 구조

```
news/
├── dashboard.html              # 웹 대시보드 (시각적 인터페이스)
├── main_workflow.py            # 통합 워크플로우 실행 스크립트
├── news_collector.py           # 뉴스 수집 모듈
├── ai_script_generator.py      # AI 대본 생성 모듈
├── tts_generator.py            # TTS 음성 생성 모듈
├── youtube_uploader.py         # 유튜브 업로드 모듈
├── client_secrets.json         # YouTube API 자격증명 (직접 생성)
├── youtube_token.pickle        # YouTube 인증 토큰 (자동 생성)
├── requirements.txt            # Python 패키지 목록
├── README.md                   # 이 문서
└── output/                     # 생성된 파일 저장 폴더
    ├── collected_news.json     # 수집된 뉴스
    ├── audio/                  # 생성된 음성 파일
    │   └── voice_*.mp3
    ├── videos/                 # 편집된 영상 파일
    │   └── video_*.mp4
    └── workflow_results_*.json # 워크플로우 결과
```

---

## ⚙️ 설정 커스터마이징

`main_workflow.py`의 `config` 딕셔너리를 수정하여 동작 방식을 조정할 수 있습니다:

```python
config = {
    # 뉴스 수집 키워드
    'keywords': ['삼성', '쿠팡', '부동산', '손흥민', 'AI', '경제'],

    # AI 서비스 선택: 'openai', 'gemini', 'anthropic', 'mock'
    'ai_service': 'openai',
    'ai_api_key': 'sk-xxxxxxxx',

    # TTS 서비스 선택: 'elevenlabs', 'google', 'azure', 'mock'
    'tts_service': 'elevenlabs',
    'tts_api_key': 'your_key',

    # YouTube 설정
    'youtube_credentials': 'client_secrets.json',

    # 하루 제작할 영상 개수
    'target_videos_per_day': 3
}
```

---

## 🔄 자동화 스케줄링

### Windows: 작업 스케줄러

1. 작업 스케줄러 열기 (`taskschd.msc`)
2. 기본 작업 만들기
3. 트리거: 매일 오전 6시
4. 작업: `python C:\Users\pc\claudecode\news\main_workflow.py`

### Mac/Linux: Crontab

```bash
# Crontab 편집
crontab -e

# 매일 오전 6시 실행
0 6 * * * cd /path/to/news && python main_workflow.py
```

---

## 📊 사용 사례

### 예시 1: 시니어 뉴스 채널

```python
config = {
    'keywords': ['연금', '건강', '부동산', '정책', '복지'],
    'target_videos_per_day': 5
}
```

### 예시 2: 경제 뉴스 채널

```python
config = {
    'keywords': ['삼성', '현대', '주식', 'SK', 'LG', '환율'],
    'target_videos_per_day': 3
}
```

### 예시 3: 스포츠 뉴스 채널

```python
config = {
    'keywords': ['손흥민', '이강인', '프리미어리그', 'K리그'],
    'target_videos_per_day': 2
}
```

---

## ⚠️ 주의사항

1. **저작권**: 뉴스 기사를 그대로 읽는 것은 저작권 문제가 될 수 있습니다. AI로 재작성하거나 출처를 명확히 표기하세요.

2. **유튜브 정책**: 반복적이고 자동화된 콘텐츠는 수익 창출에 불리할 수 있습니다. 수동 편집과 검토를 거치세요.

3. **API 비용**: OpenAI, ElevenLabs 등은 사용량에 따라 비용이 발생합니다.

4. **API 할당량**: YouTube API는 하루 10,000 쿼터 제한이 있습니다. (업로드 1회 = 약 1,600 쿼터)

---

## 🆘 문제 해결

### Q1: "ModuleNotFoundError" 오류
```bash
# 누락된 패키지 설치
pip install [패키지명]
```

### Q2: YouTube 인증 실패
- `client_secrets.json` 파일 경로 확인
- OAuth 동의 화면 설정 확인
- 테스트 사용자로 본인 이메일 추가

### Q3: TTS 음성 품질이 낮음
- ElevenLabs 사용 권장 (가장 자연스러움)
- `voice_settings`의 `stability`, `similarity_boost` 조정

### Q4: AI 대본이 이상함
- 프롬프트 수정 (`ai_script_generator.py`의 `prompt` 부분)
- GPT-4 사용 (GPT-3.5보다 품질 높음)

---

## 📈 향후 개발 계획

- [ ] Vrew API 연동으로 완전 자동 영상 편집
- [ ] 썸네일 이미지 자동 생성 (Midjourney, DALL-E)
- [ ] 여러 채널 동시 관리 기능
- [ ] 조회수 분석 및 A/B 테스트
- [ ] 웹 대시보드 백엔드 연동 (Flask/FastAPI)

---

## 📝 라이선스

MIT License

---

## 🤝 기여

Issue 및 Pull Request 환영합니다!

---

## 📧 문의

문제가 발생하거나 질문이 있으시면 Issue를 남겨주세요.
