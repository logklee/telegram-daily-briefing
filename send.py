import telegram
import openai
import os
import datetime

# 환경변수 불러오기
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=BOT_TOKEN)

# 날짜 관련 변수 정의
today = datetime.datetime.now()
weekday = today.weekday()  # 월(0) ~ 일(6)
day = today.day
today_str = today.strftime("%Y-%m-%d")

# 날짜별 프롬프트 분기
if day == 1:
    # 매월 1일: 월간 브리핑
    prompt = f"""
오늘은 {today_str}입니다. 지난 한 달 동안(전월)의 글로벌 경제 흐름을 요약해주세요.

• 주요 경제 뉴스 5건 (예: CPI, 연준 금리, 지정학, BTC 등)
• 월간 자산 흐름: KOSPI, 나스닥, BTC, 환율, 유가
• ETF 및 산업 섹터 트렌드 요약

그리고 향후 1~3개월 시계를 기준으로 중장기 포트폴리오를 구성해주세요:

- Core ETF 2~3개
- Satellite 개별종목 5~7개
- 고배당/리츠/현금성 자산 비중 제안

항상 한글로 요약하고, 가격은 원화(₩)와 달러($)로 병기 표시해주세요.
"""

elif weekday == 0:
    # 매주 월요일: 주간 브리핑
    prompt = f"""
오늘은 {today_str}입니다. 지난 주의 주요 글로벌 경제 뉴스 5건을 요약해주세요.

1️⃣ 주간 뉴스 요약
2️⃣ 주요 자산 주간 변화율 (KOSPI, 나스닥, BTC, 환율 등)
3️⃣ 이번 주 주요 이벤트 캘린더 (예: 실적 발표, FOMC, CPI 등)

그리고 2~4주 기준의 스윙 투자 종목 5개를 추천해주세요.

- 등급: 강력 매수 / 긍정 / 중립 / 보수적 접근
- 목표가 / 손절가 포함
- 한글 요약, ₩/$ 병기
"""

else:
    # 매일: 전일 뉴스 & 지수 & 단기 추천
    prompt = f"""
오늘은 {today_str}입니다. 어제 기준 글로벌 경제 뉴스 5건과 자산 종가를 요약해주세요.

📌 자산 예시:
- KOSPI, S&P500, 나스닥
- 환율(USD/KRW), 금리, WTI
- BTC, ETH

그리고 향후 1~5일 기준으로 단기 매매 아이디어를 3~5개 추천해주세요.

- 등급: 강력 매수 / 긍정 / 보수적 접근
- 진입가, 목표가, 손절가 포함
- 한글 요약 + ₩/$ 병기
"""

# GPT 호출
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "너는 한국어를 사용하는 전문 투자 전략가야."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1000,
)

briefing = response.choices[0].message.content

# 텔레그램 전송
bot.send_message(chat_id=CHAT_ID, text=f"📊 {today_str} 마켓 브리핑\n\n{briefing}")
