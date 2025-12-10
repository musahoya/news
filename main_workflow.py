"""
뉴스 기반 유튜브 자동화 - 통합 워크플로우
모든 단계를 순차적으로 실행하는 메인 스크립트
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from news_collector import NewsCollector
from ai_script_generator import AIScriptGenerator
from tts_generator import TTSGenerator
from youtube_uploader import YouTubeUploader


class NewsYouTubeAutomation:
    def __init__(self, config: dict = None):
        """
        config 예시:
        {
            'keywords': ['삼성', '쿠팡', '부동산'],
            'ai_service': 'openai',
            'ai_api_key': 'sk-xxx',
            'tts_service': 'elevenlabs',
            'tts_api_key': 'xxx',
            'youtube_credentials': 'client_secrets.json'
        }
        """
        self.config = config or self._default_config()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # 각 모듈 초기화
        self.news_collector = NewsCollector()
        self.news_collector.keywords = self.config['keywords']

        self.ai_generator = AIScriptGenerator(
            api_key=self.config.get('ai_api_key'),
            service=self.config.get('ai_service', 'mock')
        )

        self.tts_generator = TTSGenerator(
            service=self.config.get('tts_service', 'mock'),
            api_key=self.config.get('tts_api_key')
        )

        self.youtube_uploader = YouTubeUploader(
            credentials_file=self.config.get('youtube_credentials', 'client_secrets.json')
        )

    def _default_config(self) -> dict:
        """기본 설정"""
        return {
            'keywords': ['삼성', '현대', '쿠팡', '부동산', '손흥민', 'AI'],
            'ai_service': 'mock',
            'tts_service': 'mock',
            'news_count': 20,
            'target_videos_per_day': 3
        }

    def run_full_workflow(self, auto_upload: bool = False):
        """전체 워크플로우 실행"""
        print("=" * 70)
        print("🎬 뉴스 기반 유튜브 자동화 워크플로우 시작")
        print("=" * 70)

        workflow_start = datetime.now()

        # 1단계: 뉴스 수집
        print("\n📰 [1/6] 뉴스 수집 중...")
        articles = self._step1_collect_news()
        if not articles:
            print("❌ 뉴스 수집 실패. 워크플로우 중단.")
            return

        # 2단계: 상위 기사 선택
        print("\n🎯 [2/6] 영상 제작할 기사 선택...")
        selected_articles = self._step2_select_articles(articles)

        # 3~6단계: 각 기사별로 영상 제작
        results = []
        for i, article in enumerate(selected_articles, 1):
            print(f"\n{'='*70}")
            print(f"📹 기사 {i}/{len(selected_articles)}: {article['title']}")
            print(f"{'='*70}")

            result = self._process_single_article(article, auto_upload)
            results.append(result)

        # 최종 결과 출력
        workflow_end = datetime.now()
        duration = (workflow_end - workflow_start).total_seconds() / 60

        print("\n" + "=" * 70)
        print("✅ 전체 워크플로우 완료!")
        print("=" * 70)
        print(f"⏱️  소요 시간: {duration:.1f}분")
        print(f"📊 처리 완료: {len(results)}개 영상")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['article_title']}")
            print(f"   상태: {result['status']}")
            if result.get('video_url'):
                print(f"   URL: {result['video_url']}")

        # 결과 저장
        self._save_workflow_results(results)

    def _step1_collect_news(self) -> list:
        """1단계: 뉴스 수집"""
        raw_articles = self.news_collector.collect_all_news()
        trending_articles = self.news_collector.filter_trending_news(raw_articles)

        print(f"✅ {len(trending_articles)}개 트렌드 기사 수집 완료")

        # JSON 저장
        self.news_collector.save_to_json(
            trending_articles,
            filename=str(self.output_dir / "collected_news.json")
        )

        return trending_articles

    def _step2_select_articles(self, articles: list) -> list:
        """2단계: 영상 제작할 기사 선택 (관련성 점수 기준)"""
        target_count = self.config.get('target_videos_per_day', 3)
        selected = articles[:target_count]

        print(f"✅ 상위 {len(selected)}개 기사 선택:")
        for i, article in enumerate(selected, 1):
            print(f"   {i}. {article['title']} (점수: {article['relevance_score']})")

        return selected

    def _process_single_article(self, article: dict, auto_upload: bool) -> dict:
        """단일 기사에 대한 영상 제작 프로세스"""

        result = {
            'article_title': article['title'],
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        }

        try:
            # 3단계: AI 대본 생성
            print("\n  ✍️ [3/6] AI 대본 생성 중...")
            script_data = self.ai_generator.generate_youtube_script(article)
            script = script_data['script']
            print(f"  ✅ 대본 생성 완료 (예상 {script_data['estimated_duration']})")
            result['script'] = script

            # 썸네일 제목 생성
            print("\n  🎨 [3.5/6] 썸네일 제목 생성 중...")
            thumbnail_titles = self.ai_generator.generate_thumbnail_titles(article, count=10)
            best_title = thumbnail_titles[0] if thumbnail_titles else article['title']
            print(f"  ✅ 썸네일 제목: {best_title}")
            result['thumbnail_title'] = best_title

            # 메타데이터 생성
            metadata = self.ai_generator.generate_video_metadata(article, script)
            result['metadata'] = metadata

            # 4단계: TTS 음성 생성
            print("\n  🎤 [4/6] TTS 음성 생성 중...")
            tts_result = self.tts_generator.generate_audio(
                text=script,
                voice_style="professional",
                output_filename=f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            )
            print(f"  ✅ 음성 생성 완료: {tts_result['output_file']}")
            result['audio_file'] = tts_result['output_file']

            # 5단계: 영상 편집 (Vrew 연동 등 - 여기서는 Mock)
            print("\n  🎬 [5/6] 영상 편집 중...")
            video_file = self._step5_edit_video(tts_result['output_file'], script)
            print(f"  ✅ 영상 편집 완료: {video_file}")
            result['video_file'] = video_file

            # 6단계: 유튜브 업로드
            if auto_upload:
                print("\n  📤 [6/6] 유튜브 업로드 중...")
                upload_result = self.youtube_uploader.upload_video(
                    video_file=video_file,
                    title=metadata.get('title', article['title']),
                    description=metadata.get('description', ''),
                    tags=metadata.get('tags', []),
                    category_id="25",  # News & Politics
                    privacy_status="public"
                )
                print(f"  ✅ 업로드 완료: {upload_result.get('video_url', 'N/A')}")
                result['video_url'] = upload_result.get('video_url')
                result['video_id'] = upload_result.get('video_id')
            else:
                print("\n  ⏸️  [6/6] 자동 업로드 비활성화됨 (수동 업로드 필요)")

            result['status'] = 'completed'

        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)

        return result

    def _step5_edit_video(self, audio_file: str, script: str) -> str:
        """5단계: 영상 편집 (Mock)"""
        # 실제로는 Vrew, Premiere 등 편집 소프트웨어 API 연동
        # 또는 FFmpeg, MoviePy 등으로 자동 편집

        video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_path = self.output_dir / "videos" / video_filename
        video_path.parent.mkdir(parents=True, exist_ok=True)

        # Mock 비디오 파일 생성
        with open(video_path, 'w', encoding='utf-8') as f:
            f.write(f"[Mock Video File]\nAudio: {audio_file}\nScript length: {len(script)}")

        return str(video_path)

    def _save_workflow_results(self, results: list):
        """워크플로우 결과 저장"""
        output_file = self.output_dir / f"workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_videos': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 결과 저장: {output_file}")

    def schedule_daily_automation(self, target_time: str = "06:00"):
        """매일 자동 실행 스케줄링 (Windows Task Scheduler, Cron 등 사용)"""
        print(f"\n⏰ 매일 {target_time}에 자동 실행 설정")
        print("Windows: 작업 스케줄러 사용")
        print("Linux/Mac: Crontab 사용")
        print(f"  예시: 0 6 * * * python {__file__}")


# 사용 예시
if __name__ == "__main__":
    # 설정 파일 로드 (옵션)
    config = {
        'keywords': ['삼성', '쿠팡', '부동산', '손흥민', 'AI', '경제'],
        'ai_service': 'mock',  # 'openai', 'gemini', 'anthropic'
        'ai_api_key': None,
        'tts_service': 'mock',  # 'elevenlabs', 'google', 'azure'
        'tts_api_key': None,
        'youtube_credentials': 'client_secrets.json',
        'target_videos_per_day': 3
    }

    # 자동화 시스템 초기화
    automation = NewsYouTubeAutomation(config=config)

    # 전체 워크플로우 실행
    automation.run_full_workflow(auto_upload=False)

    # 결과 확인
    print("\n" + "=" * 70)
    print("📁 생성된 파일 확인:")
    print("  - output/collected_news.json (수집된 뉴스)")
    print("  - output/audio/ (생성된 음성 파일)")
    print("  - output/videos/ (편집된 영상 파일)")
    print("  - output/workflow_results_*.json (최종 결과)")
    print("=" * 70)
