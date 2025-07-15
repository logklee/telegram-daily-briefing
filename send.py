import os
import datetime
import openai
import telegram
import yfinance as yf
import requests

# API 키 및 설정
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=BOT_TOKEN)

# 날짜 설정
today = datetime.datetime.now()
today_str = today.strftime('%Y-%m-%d')
weekday = today.weekday()
day = today.day

# yfinance로 지수/자산 종가 가져오기
def get_price_yf(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="2d")
    return round(hist['Close'][-1], 2)

def get_price_coingecko(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    r = requests.get(url)
    return round(r.json()[coin_id]["usd"], 2)

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

# 📌 프롬프트 분기
if day == 1:
    # 월간
    prompt = f"""
최근 한 달 간의 글로벌 경제 흐름을 요약하고, 아래 자산 종가를 바탕으로 분석해줘:

- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

내용:
1. 전월 주요 뉴스 5건 요약
2. 주요 자산 동향 요약
3. 1~3개월 기준 중장기 포트폴리오 제안 (ETF/종목/리스크 분산 포함)
"""

elif weekday == 0:
    # 주간
    prompt = f"""
최근 1주일 간의 주요 경제 뉴스와 자산 종가를 기반으로 다음을 요약해줘:

- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

내용:
1. 지난 주 뉴스 Top 5 요약
2. 주요 지수/자산 주간 변화 분석
3. 이번 주 주요 경제 이벤트 캘린더
4. 2~4주 기준 스윙 종목 3~5개 추천 (등급, 목표가 포함)
"""

else:
    # 매일
    prompt = f"""
다음 자산의 전일 종가를 바탕으로 경제 뉴스 요약 및 단기 종목 추천을 해줘:

- KOSPI: {prices['KOSPI']} ₩
- S&P500: {prices['S&P500']} $
- NASDAQ: {prices['NASDAQ']} $
- USD/KRW: {prices['USD/KRW']} ₩
- WTI: {prices['WTI']} $
- BTC: {prices['BTC']} $
- ETH: {prices['ETH']} $

내용:
1. 전일 주요 뉴스 5건 요약
2. 시장 흐름 분석
3. 1~5일 기준 단기 매매 아이디어 3~5개 추천 (진입가, 목표가, 손절가 포함)
4. 등급: 강력 매수 / 긍정 / 보수적 접근
"""

# GPT 호출
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 전문 투자 전략가이자 리서치 애널리스트야. 항상 한글로 작성해."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1200,
)

result = response.choices[0].message.content

# 텔레그램 전송
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{result}")
