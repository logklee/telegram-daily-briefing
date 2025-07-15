import os
import datetime
import openai
import telegram
import yfinance as yf
import requests
import feedparser

# 환경 변수
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 설정
openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=BOT_TOKEN)
today = datetime.datetime.now()
today_str = today.strftime('%Y-%m-%d')

# 자산 데이터 수집
def get_price_yf(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="2d")
    return round(hist['Close'][-1], 2)

def get_price_coingecko(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    r = requests.get(url)
    return round(r.json()[coin_id]["usd"], 2)

prices = {
    "KOSPI": get_price_yf("^KS11"),
    "S&P500": get_price_yf("^GSPC"),
    "NASDAQ": get_price_yf("^IXIC"),
    "USD/KRW": get_price_yf("USDKRW=X"),
    "WTI": get_price_yf("CL=F"),
    "BTC": get_price_coingecko("bitcoin"),
    "ETH": get_price_coingecko("ethereum"),
}

# 뉴스 헤드라인 수집
def fetch_news_headlines(max_items=5):
    feed = feedparser.parse("https://news.google.com/rss/search?q=증시+OR+경제+OR+코스피+OR+비트코인&hl=ko&gl=KR&ceid=KR:ko")
    headlines = []
    for entry in feed.entries[:max_items]:
        source = entry.source.title if 'source' in entry else 'Google News'
        headlines.append(f"- {entry.title} ({source})")
    return "\n".join(headlines)

headlines = fetch_news_headlines()

# 프롬프트 생성
prompt = f"""
🗓 [데일리 브리프 | {today_str} 09:00 KST]

[헤드라인 목록]
{headlines}

[자산 종가 정보]
- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

이 정보를 기반으로 다음을 생성해줘:

1️⃣ 어제의 시장 흐름 요약 (3~5줄)

2️⃣ 아래 형식으로 자산 종가 테이블 생성
| 자산 | 종가 | 일변동 | YTD | 비고 | 출처 |
|------|------|--------|-----|------|------|

3️⃣ 단기 추천 종목 테이블 (1~5일 시계)
| 등급 | 종목명 | 현재가 | 진입범위 | 목표가 | 손절가 | 비고 |
|------|--------|---------|-----------|--------|--------|------|

📌 모든 표는 Markdown 형식
📌 수치는 반드시 채워야 하며, 가격은 ₩ 또는 $로 병기
📌 모든 응답은 한국어로 작성
📌 뉴스 및 수치 기반으로 신뢰도 있게 요약
"""

# GPT 요청
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 실시간 데이터를 바탕으로 요약 리포트를 작성하는 한국어 금융 애널리스트야."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1600,
)

# 텔레그램 전송
result = response.choices[0].message.content
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{result}")