"""
TTS (Text-to-Speech) 음성 생성
- ElevenLabs, Google TTS, Azure TTS 지원
- 자연스러운 AI 보이스 생성
"""

import requests
import json
from pathlib import Path
from typing import Dict

class TTSGenerator:
    def __init__(self, service: str = "elevenlabs", api_key: str = None):
        """
        service: "elevenlabs", "google", "azure"
        """
        self.service = service
        self.api_key = api_key
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_audio(self, text: str, voice_style: str = "professional",
                      output_filename: str = "voice_output.mp3") -> Dict:
        """텍스트를 음성으로 변환"""

        if self.service == "elevenlabs":
            return self._generate_elevenlabs(text, voice_style, output_filename)
        elif self.service == "google":
            return self._generate_google_tts(text, voice_style, output_filename)
        elif self.service == "azure":
            return self._generate_azure_tts(text, voice_style, output_filename)
        else:
            return self._generate_mock(text, output_filename)

    def _generate_elevenlabs(self, text: str, voice_style: str,
                            output_filename: str) -> Dict:
        """ElevenLabs TTS API 호출"""

        # 음성 스타일에 따른 voice_id 매핑
        voice_mapping = {
            "professional": "21m00Tcm4TlvDq8ikWAM",  # Rachel (여성, 전문적)
            "friendly": "AZnzlk1XvdvUeBnXmlld",     # Domi (여성, 친근한)
            "energetic": "TxGEqnHWrfWFTfGW9XjX"    # Josh (남성, 활기찬)
        }

        voice_id = voice_mapping.get(voice_style, voice_mapping["professional"])

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # 다국어 지원
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                output_path = self.output_dir / output_filename
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return {
                    'status': 'success',
                    'output_file': str(output_path),
                    'service': 'elevenlabs',
                    'voice_style': voice_style,
                    'duration_estimate': len(text) // 150  # 분 단위 추정
                }
            else:
                print(f"ElevenLabs API 오류: {response.status_code} - {response.text}")
                return self._generate_mock(text, output_filename)

        except Exception as e:
            print(f"ElevenLabs API 호출 실패: {e}")
            return self._generate_mock(text, output_filename)

    def _generate_google_tts(self, text: str, voice_style: str,
                            output_filename: str) -> Dict:
        """Google Cloud TTS API 호출"""

        from google.cloud import texttospeech

        try:
            client = texttospeech.TextToSpeechClient()

            # 음성 스타일에 따른 설정
            voice_mapping = {
                "professional": {"name": "ko-KR-Standard-A", "gender": "FEMALE"},
                "friendly": {"name": "ko-KR-Standard-B", "gender": "FEMALE"},
                "energetic": {"name": "ko-KR-Standard-C", "gender": "MALE"}
            }

            voice_config = voice_mapping.get(voice_style, voice_mapping["professional"])

            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name=voice_config["name"],
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice_config["gender"])
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # 속도 (0.25 ~ 4.0)
                pitch=0.0  # 음높이 (-20.0 ~ 20.0)
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            output_path = self.output_dir / output_filename
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)

            return {
                'status': 'success',
                'output_file': str(output_path),
                'service': 'google',
                'voice_style': voice_style,
                'duration_estimate': len(text) // 150
            }

        except Exception as e:
            print(f"Google TTS API 호출 실패: {e}")
            return self._generate_mock(text, output_filename)

    def _generate_azure_tts(self, text: str, voice_style: str,
                           output_filename: str) -> Dict:
        """Azure Cognitive Services TTS API 호출"""

        # 음성 스타일에 따른 설정
        voice_mapping = {
            "professional": "ko-KR-SunHiNeural",
            "friendly": "ko-KR-InJoonNeural",
            "energetic": "ko-KR-BongJinNeural"
        }

        voice_name = voice_mapping.get(voice_style, voice_mapping["professional"])

        url = "https://koreacentral.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
        }

        ssml = f"""
        <speak version='1.0' xml:lang='ko-KR'>
            <voice xml:lang='ko-KR' name='{voice_name}'>
                {text}
            </voice>
        </speak>
        """

        try:
            response = requests.post(url, headers=headers, data=ssml.encode('utf-8'), timeout=120)

            if response.status_code == 200:
                output_path = self.output_dir / output_filename
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return {
                    'status': 'success',
                    'output_file': str(output_path),
                    'service': 'azure',
                    'voice_style': voice_style,
                    'duration_estimate': len(text) // 150
                }
            else:
                print(f"Azure TTS API 오류: {response.status_code}")
                return self._generate_mock(text, output_filename)

        except Exception as e:
            print(f"Azure TTS API 호출 실패: {e}")
            return self._generate_mock(text, output_filename)

    def _generate_mock(self, text: str, output_filename: str) -> Dict:
        """Mock 음성 생성 (테스트용)"""
        output_path = self.output_dir / output_filename

        # 더미 파일 생성
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"[Mock Audio File]\nText: {text[:100]}...\nDuration: {len(text) // 150} minutes")

        print(f"Mock 음성 파일 생성: {output_path}")

        return {
            'status': 'success (mock)',
            'output_file': str(output_path),
            'service': 'mock',
            'duration_estimate': len(text) // 150,
            'text_length': len(text)
        }

    def split_text_for_tts(self, text: str, max_length: int = 5000) -> list:
        """긴 텍스트를 TTS 제한 길이에 맞게 분할"""
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def merge_audio_files(self, audio_files: list, output_filename: str = "merged_audio.mp3"):
        """여러 음성 파일을 하나로 병합 (pydub 사용)"""
        try:
            from pydub import AudioSegment

            combined = AudioSegment.empty()
            for audio_file in audio_files:
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio

            output_path = self.output_dir / output_filename
            combined.export(output_path, format="mp3")

            return str(output_path)

        except ImportError:
            print("pydub가 설치되지 않았습니다. pip install pydub 실행 필요")
            return None
        except Exception as e:
            print(f"오디오 병합 실패: {e}")
            return None


# 사용 예시
if __name__ == "__main__":
    # Mock 모드로 테스트
    tts = TTSGenerator(service="mock")

    sample_script = """
여러분, 안녕하세요. 오늘은 정말 중요한 소식을 가지고 왔습니다.

최근 삼성전자가 반도체 분야에 50조 원이라는 엄청난 금액을 투자하기로 결정했다는 소식입니다.
이는 우리 경제와 주식 시장에 큰 영향을 미칠 것으로 보입니다.

먼저 이 투자의 배경부터 살펴보겠습니다...
(중략)

오늘 영상이 도움이 되셨다면 구독과 좋아요 부탁드립니다. 감사합니다.
    """

    print("🎤 TTS 음성 생성 테스트")
    print("=" * 50)

    # 음성 생성
    result = tts.generate_audio(
        text=sample_script,
        voice_style="professional",
        output_filename="test_voice.mp3"
    )

    print(f"\n✅ 생성 완료:")
    print(f"  - 서비스: {result['service']}")
    print(f"  - 파일: {result['output_file']}")
    print(f"  - 예상 길이: 약 {result['duration_estimate']}분")
    print(f"  - 상태: {result['status']}")

    # 실제 API 사용 예시 (주석 처리)
    # tts_elevenlabs = TTSGenerator(service="elevenlabs", api_key="YOUR_API_KEY")
    # result = tts_elevenlabs.generate_audio(sample_script, "professional")
