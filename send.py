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
        headlines.append(f"- {entry.title} – {entry.source.title if 'source' in entry else 'Google News'}")
    return "\n".join(headlines)

headlines = fetch_news_headlines()

# GPT 프롬프트 (전문가 보고서 형식)
prompt = f"""
🗓 [데일리 브리프 | {today_str} 09:00 KST]

아래는 어제의 자산 종가 및 주요 뉴스 헤드라인입니다.

[헤드라인 목록]
{headlines}

[지수 및 자산 종가]
- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

위의 내용을 바탕으로 다음 항목을 각각 구성해줘:

1️⃣ 전일 주요 뉴스 Top 5 (뉴스 제목 요약 + 출처 이름 포함)

2️⃣ 지수·자산 스냅샷 (아래 형식으로 표로 작성)
| 자산 | 종가 | 일변동 | YTD | 비고 | 출처 |
|------|------|--------|-----|------|------|

3️⃣ 단기 추천 종목 (1~5일 시계)
- 최소 3종목 이상, 최대 6종목
- 아래 형식의 표로 작성
| 등급 | 종목명 | 현재가 | 진입범위 | 목표가 | 손절가 | 비고 |
|------|--------|---------|-----------|--------|--------|------|

4️⃣ 모든 응답은 한글로 작성하고, 가격은 원화(₩) 또는 달러($)로 병기해줘.
5️⃣ 뉴스 출처는 반드시 포함해줘 (예: Reuters, 조선일보, Bloomberg 등).
6️⃣ 표는 Markdown 표 형식을 지켜줘.
"""

# GPT 요청
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 실시간 데이터 기반으로 요약과 분석을 하는 한국어 금융 애널리스트야."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1600,
)

# 텔레그램 전송
result = response.choices[0].message.content
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{result}")