FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install unzip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN unzip -o swiftie-lyric-bot/data/taylor_swift_tracks.csv.zip -d swiftie-lyric-bot/data
RUN unzip -o swiftie-lyric-bot/data/lyrics.csv.zip -d swiftie-lyric-bot/data
RUN unzip -o swiftie-lyric-bot/data/lyrics-chunks.csv.zip -d swiftie-lyric-bot/data

EXPOSE 8501

# ENTRYPOINT ["streamlit", "run", "swiftie-lyric-bot/chatbot/bot.py", "--server.port=8501", "--server.address=0.0.0.0"]
RUN chmod +x swiftie-lyric-bot/run_bot.sh

ENTRYPOINT ["sh", "swiftie-lyric-bot/run_bot.sh"]