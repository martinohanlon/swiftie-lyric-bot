#!/bin/bash

echo "Building graph..."
python swiftie-lyric-bot/data/build_graph.py
echo "Starting Chatbot"
streamlit run swiftie-lyric-bot/chatbot/bot.py --server.port=8501 --server.address=0.0.0.0