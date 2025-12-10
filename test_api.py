"""
API 연결 테스트 스크립트
- Gemini, OpenAI, Anthropic API 연결 확인
- 대본 생성 테스트
"""

import requests
import json

def test_gemini_api(api_key: str):
    """Google Gemini API 테스트"""
    print("\n" + "="*60)
    print("🧪 Gemini API 테스트 시작")
    print("="*60)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    test_article = {
        'title': '삼성전자, 반도체 분야 50조 투자 발표',
        'description': '삼성전자가 차세대 반도체 생산을 위해 50조 원 규모의 대규모 투자를 결정했습니다.'
    }

    prompt = f"""
당신은 시니어층(40~60대)을 대상으로 하는 유튜브 뉴스 채널의 전문 작가입니다.

아래 뉴스 기사를 바탕으로 8~10분 분량의 유튜브 영상 대본을 작성해주세요.

[뉴스 기사]
제목: {test_article['title']}
내용: {test_article['description']}

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

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        print(f"📤 요청 전송 중...")
        print(f"URL: {url[:80]}...")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"📥 응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 응답 구조 출력
            print(f"\n✅ API 연결 성공!")
            print(f"\n📋 응답 구조:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")

            # 대본 추출
            try:
                script = result['candidates'][0]['content']['parts'][0]['text']
                print(f"\n📝 생성된 대본 (처음 500자):")
                print("-" * 60)
                print(script[:500])
                print("-" * 60)
                print(f"\n총 대본 길이: {len(script)}자 (약 {len(script)//150}분 분량)")

                return True, script

            except KeyError as e:
                print(f"❌ 응답 파싱 오류: {e}")
                print(f"전체 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False, None
        else:
            print(f"\n❌ API 호출 실패!")
            print(f"상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")

            # 일반적인 오류 원인 안내
            if response.status_code == 400:
                print("\n💡 400 오류 원인:")
                print("  - API 키 형식이 잘못되었을 수 있습니다")
                print("  - 요청 본문 형식이 잘못되었을 수 있습니다")
            elif response.status_code == 403:
                print("\n💡 403 오류 원인:")
                print("  - API 키가 유효하지 않습니다")
                print("  - Gemini API가 활성화되지 않았습니다")
                print("  - https://makersuite.google.com/app/apikey 에서 키 확인")
            elif response.status_code == 429:
                print("\n💡 429 오류 원인:")
                print("  - API 사용량 한도 초과")
                print("  - 잠시 후 다시 시도하세요")

            return False, None

    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과 (60초)")
        return False, None
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False, None


def test_openai_api(api_key: str):
    """OpenAI API 테스트"""
    print("\n" + "="*60)
    print("🧪 OpenAI API 테스트 시작")
    print("="*60)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "안녕하세요. 간단한 인사말로 응답해주세요."}],
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        print(f"📥 응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ OpenAI API 연결 성공!")
            print(f"응답: {message}")
            return True
        else:
            print(f"❌ OpenAI API 호출 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False


def test_thumbnail_generation(api_key: str, article_title: str):
    """썸네일 제목 생성 테스트"""
    print("\n" + "="*60)
    print("🧪 썸네일 제목 생성 테스트")
    print("="*60)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    prompt = f"""
아래 뉴스 제목을 바탕으로 유튜브 썸네일에 들어갈 강력한 후킹 문구를 10개 생성해주세요.

뉴스 제목: {article_title}

[요구사항]
1. 15자 이내로 간결하게
2. 충격, 궁금증 유발
3. 다양한 스타일 사용:
   - 질문형: "이게 가능해?"
   - 숫자형: "50조 투자"
   - 충격형: "경악! ~~"
   - 반전형: "알고보니..."

각 제목만 번호와 함께 출력해주세요. 다른 설명은 하지 마세요.
    """

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']

            print(f"✅ 썸네일 제목 생성 성공!")
            print(f"\n생성된 제목들:")
            print("-" * 60)
            print(text)
            print("-" * 60)

            return True, text
        else:
            print(f"❌ 실패: {response.status_code}")
            return False, None

    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False, None


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 API 연결 테스트 도구")
    print("=" * 60)

    print("\n이 스크립트는 각 API의 연결 상태를 테스트합니다.")
    print("\n테스트할 API를 선택하세요:")
    print("1. Google Gemini (추천)")
    print("2. OpenAI GPT")
    print("3. 둘 다 테스트")

    choice = input("\n선택 (1-3): ").strip()

    if choice in ['1', '3']:
        api_key = input("\nGemini API 키를 입력하세요: ").strip()
        if api_key:
            # 대본 생성 테스트
            success, script = test_gemini_api(api_key)

            if success:
                # 썸네일 제목 생성 테스트
                test_thumbnail_generation(api_key, "삼성전자, 반도체 분야 50조 투자 발표")

                print("\n" + "="*60)
                print("✅ Gemini API 모든 테스트 통과!")
                print("="*60)
                print("\n💾 이 API 키를 main_workflow.py에 설정하세요:")
                print(f"\nconfig = {{")
                print(f"    'ai_service': 'gemini',")
                print(f"    'ai_api_key': '{api_key}'")
                print(f"}}")
            else:
                print("\n" + "="*60)
                print("❌ Gemini API 테스트 실패")
                print("="*60)
                print("\n📝 해결 방법:")
                print("1. https://makersuite.google.com/app/apikey 접속")
                print("2. 'Create API key' 클릭")
                print("3. 생성된 키를 복사하여 사용")
        else:
            print("❌ API 키가 입력되지 않았습니다.")

    if choice in ['2', '3']:
        api_key = input("\nOpenAI API 키를 입력하세요 (sk-...): ").strip()
        if api_key:
            test_openai_api(api_key)
        else:
            print("❌ API 키가 입력되지 않았습니다.")

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)
