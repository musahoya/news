"""
뉴스 수집 자동화 스크립트
- 네이버 뉴스, Google News RSS 등에서 트렌드 기사 수집
- 키워드 기반 필터링 및 우선순위 지정
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import json
from typing import List, Dict

class NewsCollector:
    def __init__(self):
        self.keywords = [
            "삼성", "현대", "쿠팡", "배달", "부동산",
            "주식", "경제", "정책", "손흥민", "AI"
        ]
        self.collected_news = []

    def fetch_naver_news(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """네이버 뉴스 검색 API를 통한 뉴스 수집"""
        # 실제 구현 시 네이버 API 키 필요
        url = f"https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": "YOUR_CLIENT_ID",  # 실제 키로 교체
            "X-Naver-Client-Secret": "YOUR_CLIENT_SECRET"
        }
        params = {
            "query": keyword,
            "display": max_results,
            "sort": "sim"  # sim: 정확도순, date: 날짜순
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []
                for item in data.get('items', []):
                    articles.append({
                        'title': self._clean_html(item['title']),
                        'description': self._clean_html(item['description']),
                        'link': item['link'],
                        'pub_date': item['pubDate'],
                        'keyword': keyword,
                        'source': 'naver'
                    })
                return articles
        except Exception as e:
            print(f"네이버 뉴스 수집 오류 ({keyword}): {e}")
        return []

    def fetch_google_news_rss(self, keyword: str) -> List[Dict]:
        """Google News RSS를 통한 뉴스 수집 (API 키 불필요)"""
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"

        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'description': entry.get('summary', ''),
                    'link': entry.link,
                    'pub_date': entry.get('published', ''),
                    'keyword': keyword,
                    'source': 'google_news'
                })
            return articles
        except Exception as e:
            print(f"Google 뉴스 수집 오류 ({keyword}): {e}")
        return []

    def scrape_article_content(self, url: str) -> str:
        """기사 본문 스크래핑"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')

            # 일반적인 기사 본문 태그 시도
            article_body = None
            for selector in ['article', '.article_body', '#articleBodyContents', '.news_end']:
                article_body = soup.select_one(selector)
                if article_body:
                    break

            if article_body:
                # 스크립트, 스타일 제거
                for tag in article_body(['script', 'style', 'iframe']):
                    tag.decompose()
                return article_body.get_text(strip=True, separator='\n')

            return ""
        except Exception as e:
            print(f"기사 스크래핑 오류: {e}")
            return ""

    def collect_all_news(self) -> List[Dict]:
        """모든 키워드에 대해 뉴스 수집"""
        all_articles = []

        for keyword in self.keywords:
            print(f"🔍 '{keyword}' 키워드 뉴스 수집 중...")

            # Google News RSS 사용 (API 키 불필요)
            articles = self.fetch_google_news_rss(keyword)
            all_articles.extend(articles)

            # 네이버 API 사용 시 (주석 해제)
            # articles = self.fetch_naver_news(keyword, max_results=5)
            # all_articles.extend(articles)

        print(f"✅ 총 {len(all_articles)}개 기사 수집 완료")
        return all_articles

    def filter_trending_news(self, articles: List[Dict], min_relevance: float = 0.5) -> List[Dict]:
        """트렌드 및 관련성 기반 필터링"""
        # 간단한 점수 시스템: 제목에 키워드가 많을수록 높은 점수
        scored_articles = []

        for article in articles:
            score = 0
            title_lower = article['title'].lower()

            # 키워드 매칭 점수
            for keyword in self.keywords:
                if keyword.lower() in title_lower:
                    score += 1

            # 최신성 점수 (추가 가능)
            score += 0.5

            article['relevance_score'] = score
            if score >= min_relevance:
                scored_articles.append(article)

        # 점수 기준 정렬
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_articles

    def save_to_json(self, articles: List[Dict], filename: str = "collected_news.json"):
        """수집된 뉴스를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'collected_at': datetime.now().isoformat(),
                'total_count': len(articles),
                'articles': articles
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 {filename}에 저장 완료")

    @staticmethod
    def _clean_html(text: str) -> str:
        """HTML 태그 제거"""
        return BeautifulSoup(text, 'html.parser').get_text()


# 사용 예시
if __name__ == "__main__":
    collector = NewsCollector()

    # 1. 뉴스 수집
    raw_articles = collector.collect_all_news()

    # 2. 트렌드 필터링
    trending_articles = collector.filter_trending_news(raw_articles)

    # 3. 상위 5개 기사 본문 수집
    print("\n📰 상위 5개 트렌드 기사:")
    for i, article in enumerate(trending_articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   키워드: {article['keyword']} | 점수: {article['relevance_score']}")
        print(f"   링크: {article['link']}")

        # 본문 수집 (선택적)
        # content = collector.scrape_article_content(article['link'])
        # article['content'] = content[:500]  # 처음 500자만

    # 4. JSON 저장
    collector.save_to_json(trending_articles[:20])
