import telegram
import openai
import os
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

today = datetime.datetime.now().strftime('%Y-%m-%d')

prompt = f"""{today} 기준으로 한국·미국·암호화폐 주요 경제 뉴스 Top 5를 요약해줘.
그리고 추천 종목 6개(강력 매수/긍정적/보수적 등급 포함)를 한글로 정리해줘.
모든 수치는 원화(₩) 및 달러($) 병기 표시하고, 한글로만 작성해줘."""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "너는 전문 투자 분석가야."},
              {"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=800,
)

briefing = response.choices[0].message.content
bot = telegram.Bot(token=BOT_TOKEN)
bot.send_message(chat_id=CHAT_ID, text=briefing)
