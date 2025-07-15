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
weekday = today.weekday()
day = today.day

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

# 뉴스 헤드라인 수집 (Google Finance RSS)
def fetch_news_headlines(max_items=5):
    feed = feedparser.parse("https://news.google.com/rss/search?q=증시+OR+경제+OR+코스피+OR+비트코인&hl=ko&gl=KR&ceid=KR:ko")
    headlines = []
    for entry in feed.entries[:max_items]:
        headlines.append(f"- {entry.title}")
    return "\n".join(headlines)

headlines = fetch_news_headlines()

# 프롬프트 생성
prompt = f"""
다음은 최근 주요 경제 뉴스 헤드라인입니다:
{headlines}

그리고 다음은 어제 자산 종가입니다:

- KOSPI: {prices['KOSPI']} 원
- S&P500: {prices['S&P500']} 달러
- NASDAQ: {prices['NASDAQ']} 달러
- USD/KRW: {prices['USD/KRW']} 원
- WTI: {prices['WTI']} 달러
- BTC: {prices['BTC']} 달러
- ETH: {prices['ETH']} 달러

이 정보를 기반으로:

1. 시장 흐름 및 심리를 요약해주세요 (3~5줄)
2. 관련 단기 종목 추천 3~5개 제공 (등급, 진입가, 목표가, 손절가 포함)
3. 모든 응답은 한글로, 가격은 원 또는 달러로 표기해주세요.
"""

# GPT 요청
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 실시간 데이터를 받아 요약하는 한국어 투자 전략가야."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1200,
)

# 텔레그램 전송
result = response.choices[0].message.content
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{result}")