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
openai.api_key = OPENAI_API_KEY

# 날짜 설정
today = datetime.datetime.now()
today_str = today.strftime('%Y-%m-%d')

# 텔레그램
bot = telegram.Bot(token=BOT_TOKEN)

# 자산 가격 수집
def get_price_yf(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="2d")
    return round(hist['Close'][-1], 2)

def get_price_coingecko(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    r = requests.get(url)
    return round(r.json()[coin_id]["usd"], 2)

# 뉴스 헤드라인 수집
def fetch_news_headlines(max_items=5):
    feed = feedparser.parse("https://news.google.com/rss/search?q=증시+OR+경제+OR+코스피+OR+비트코인&hl=ko&gl=KR&ceid=KR:ko")
    headlines = []
    for entry in feed.entries[:max_items]:
        source = entry.source.title if 'source' in entry else 'Google News'
        headlines.append(f"- {entry.title} ({source})")
    return "\n".join(headlines)

# 자산 수집
prices = {
    "KOSPI": get_price_yf("^KS11"),
    "S&P500": get_price_yf("^GSPC"),
    "NASDAQ": get_price_yf("^IXIC"),
    "USD/KRW": get_price_yf("USDKRW=X"),
    "WTI": get_price_yf("CL=F"),
    "BTC": get_price_coingecko("bitcoin"),
    "ETH": get_price_coingecko("ethereum"),
}
headlines = fetch_news_headlines()

# GPT 프롬프트
prompt = f"""
🗓 [데일리 브리프 | {today_str} 09:00 KST]

[전일 주요 뉴스 Top 5 헤드라인]
{headlines}

[지수 및 자산 종가]
- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

위 정보를 기반으로 아래 세 가지 섹션을 작성해줘:

1️⃣ 어제의 시장 흐름 요약 (3~5줄)

2️⃣ 자산 종가 표 (아래 형식에 따라 채워줘)
| 자산 | 종가 | 일변동 | YTD | 비고 | 출처 |
|------|------|--------|-----|------|------|

3️⃣ Daily Picks (1~5일 단기 종목 추천)
GPT가 추론하여 작성하되, 표를 아래 형식으로 채워줘
| 등급 | 종목명 | 현재가 | 진입범위 | 목표가 | 손절가 | 비고 |
|------|--------|---------|-----------|--------|--------|------|

✅ 가격은 반드시 수치로 채우고, 마크다운 형식으로 작성
✅ 모든 내용은 한글로
✅ 출처는 Reuters, 조선일보, Bloomberg 등 적절히 삽입
"""

# GPT 요청
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 실시간 데이터 기반으로 마켓 리포트를 작성하는 한국어 금융 애널리스트야."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1800,
)

# 전송
result = response.choices[0].message.content
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{result}")