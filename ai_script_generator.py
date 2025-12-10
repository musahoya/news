"""
AI 기반 유튜브 대본 및 썸네일 제목 생성
- OpenAI GPT, Google Gemini, Anthropic Claude 등 활용
- 뉴스 기사를 유튜브 대본으로 변환
- 후킹 강한 썸네일 제목 생성
"""

import requests
import json
from typing import Dict, List
from datetime import datetime

class AIScriptGenerator:
    def __init__(self, api_key: str = None, service: str = "openai"):
        """
        service: "openai", "gemini", "anthropic" 중 선택
        """
        self.api_key = api_key
        self.service = service

    def generate_youtube_script(self, article: Dict) -> Dict:
        """뉴스 기사를 유튜브 대본으로 변환"""

        prompt = f"""
당신은 시니어층(40~60대)을 대상으로 하는 유튜브 뉴스 채널의 전문 작가입니다.

아래 뉴스 기사를 바탕으로 8~10분 분량의 유튜브 영상 대본을 작성해주세요.

[뉴스 기사]
제목: {article['title']}
내용: {article.get('description', '')}

[대본 작성 요구사항]
1. **도입부 (30초)**: 강력한 후킹 멘트로 시작 (예: "여러분, 이거 아십니까?", "충격적인 소식입니다")
2. **본문 (7분)**:
   - 기사 내용을 쉽고 자세하게 설명
   - 전문 용어는 풀어서 설명
   - 중간중간 시청자 몰입 유도 멘트 삽입
3. **마무리 (30초)**:
   - 핵심 요약
   - 구독, 좋아요, 알림 설정 요청
   - 다음 영상 예고

[톤 및 스타일]
- 전달형, 존중하는 어조
- "여러분", "~입니다" 등 정중한 표현
- 감정적 어필보다는 사실 중심

대본만 출력해주세요.
        """

        script = self._call_ai_api(prompt)

        return {
            'article_title': article['title'],
            'script': script,
            'estimated_duration': '8-10분',
            'generated_at': datetime.now().isoformat()
        }

    def generate_thumbnail_titles(self, article: Dict, count: int = 10) -> List[str]:
        """CTR 높은 썸네일 제목 생성"""

        prompt = f"""
아래 뉴스 제목을 바탕으로 유튜브 썸네일에 들어갈 강력한 후킹 문구를 {count}개 생성해주세요.

뉴스 제목: {article['title']}

[요구사항]
1. 15자 이내로 간결하게
2. 충격, 궁금증 유발
3. 다양한 스타일 사용:
   - 질문형: "이게 가능해?"
   - 숫자형: "00억 날렸다"
   - 충격형: "경악! ~~"
   - 반전형: "알고보니..."

각 제목만 번호와 함께 출력해주세요.
        """

        response = self._call_ai_api(prompt)

        # 응답에서 제목 리스트 추출
        titles = [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
        titles = [title.split('.', 1)[-1].strip() if '.' in title[:5] else title for title in titles]

        return titles[:count]

    def generate_video_metadata(self, article: Dict, script: str) -> Dict:
        """유튜브 영상 메타데이터 생성 (제목, 설명, 태그)"""

        prompt = f"""
아래 뉴스와 대본을 바탕으로 유튜브 영상 메타데이터를 생성해주세요.

뉴스 제목: {article['title']}
대본: {script[:500]}...

다음 형식으로 출력:
VIDEO_TITLE: [60자 이내 영상 제목]
DESCRIPTION: [200자 정도 영상 설명, 뉴스 출처 포함]
TAGS: [관련 태그 10개, 쉼표로 구분]
        """

        response = self._call_ai_api(prompt)

        # 응답 파싱
        metadata = {}
        for line in response.split('\n'):
            if line.startswith('VIDEO_TITLE:'):
                metadata['title'] = line.replace('VIDEO_TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                metadata['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('TAGS:'):
                tags_str = line.replace('TAGS:', '').strip()
                metadata['tags'] = [tag.strip() for tag in tags_str.split(',')]

        return metadata

    def _call_ai_api(self, prompt: str) -> str:
        """AI API 호출 (OpenAI, Gemini, Anthropic)"""

        if self.service == "openai":
            return self._call_openai(prompt)
        elif self.service == "gemini":
            return self._call_gemini(prompt)
        elif self.service == "anthropic":
            return self._call_anthropic(prompt)
        else:
            return self._call_mock(prompt)

    def _call_openai(self, prompt: str) -> str:
        """OpenAI GPT API 호출"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",  # 또는 gpt-4, gpt-3.5-turbo
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"OpenAI API 오류: {response.status_code}")
                return self._call_mock(prompt)
        except Exception as e:
            print(f"OpenAI API 호출 실패: {e}")
            return self._call_mock(prompt)

    def _call_gemini(self, prompt: str) -> str:
        """Google Gemini API 호출"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API 오류: {response.status_code}")
                return self._call_mock(prompt)
        except Exception as e:
            print(f"Gemini API 호출 실패: {e}")
            return self._call_mock(prompt)

    def _call_anthropic(self, prompt: str) -> str:
        """Anthropic Claude API 호출"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()['content'][0]['text']
            else:
                print(f"Anthropic API 오류: {response.status_code}")
                return self._call_mock(prompt)
        except Exception as e:
            print(f"Anthropic API 호출 실패: {e}")
            return self._call_mock(prompt)

    def _call_mock(self, prompt: str) -> str:
        """Mock 응답 (테스트용)"""
        if "썸네일" in prompt or "제목" in prompt:
            return """
1. 이거 실화인가요?
2. 충격! 00억 날렸다
3. 결국 터졌습니다
4. 알고 보니 대박
5. 지금 당장 확인하세요
6. 99% 모르는 사실
7. 뒤늦은 후회
8. 전문가도 놀란
9. 이제야 밝혀진 진실
10. 반드시 알아야 할
            """
        elif "VIDEO_TITLE" in prompt or "메타데이터" in prompt:
            return """
VIDEO_TITLE: [충격] 삼성전자 000억 투자 결정! 주가 영향은?
DESCRIPTION: 삼성전자가 반도체 분야에 대규모 투자를 결정했습니다. 이번 투자가 국내 경제와 주가에 미칠 영향을 자세히 분석합니다. 출처: 네이버뉴스
TAGS: 삼성전자, 반도체, 투자, 주가, 경제뉴스, 시니어뉴스, 한국경제, 기술주, 증시, 재테크
            """
        else:
            return """
여러분, 안녕하세요. 오늘은 정말 중요한 소식을 가지고 왔습니다.

[도입부]
혹시 여러분, 이 소식 들어보셨나요? 최근 많은 분들이 관심을 가지고 계신 내용인데요, 오늘 자세히 알아보도록 하겠습니다.

[본문]
먼저 사건의 전말을 말씀드리자면... (중략)

이는 우리 생활에 어떤 영향을 미칠까요? 전문가들은...

[마무리]
오늘 영상이 도움이 되셨다면 구독과 좋아요, 알림 설정 부탁드립니다.
다음 영상에서는 더 유익한 정보로 찾아뵙겠습니다. 감사합니다.
            """


# 사용 예시
if __name__ == "__main__":
    # API 키 없이 Mock 모드로 테스트
    generator = AIScriptGenerator(service="mock")

    # 샘플 뉴스 데이터
    sample_article = {
        'title': '쿠팡, 새벽배송 확대… 전국 95% 지역 커버',
        'description': '쿠팡이 로켓배송 서비스 지역을 전국 95%까지 확대한다고 발표했다.'
    }

    # 1. 대본 생성
    print("📝 유튜브 대본 생성 중...")
    script_data = generator.generate_youtube_script(sample_article)
    print(script_data['script'][:300] + "...\n")

    # 2. 썸네일 제목 생성
    print("🎨 썸네일 제목 10개 생성 중...")
    thumbnail_titles = generator.generate_thumbnail_titles(sample_article, count=10)
    for i, title in enumerate(thumbnail_titles, 1):
        print(f"{i}. {title}")

    # 3. 메타데이터 생성
    print("\n📊 영상 메타데이터 생성 중...")
    metadata = generator.generate_video_metadata(sample_article, script_data['script'])
    print(f"제목: {metadata.get('title', 'N/A')}")
    print(f"설명: {metadata.get('description', 'N/A')}")
    print(f"태그: {', '.join(metadata.get('tags', []))}")

    # 4. 결과 저장
    output = {
        'article': sample_article,
        'script': script_data,
        'thumbnail_titles': thumbnail_titles,
        'metadata': metadata
    }

    with open('generated_content.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\n💾 generated_content.json 저장 완료")
