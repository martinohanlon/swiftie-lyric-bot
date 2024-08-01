import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import YouTubeSearchTool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory

from llm import llm
from graph import graph
from lyrics import get_lyrics
from song_data import get_song_data
from utils import get_session_id

import logging
logging.getLogger().setLevel(logging.ERROR)


youtube = YouTubeSearchTool()

def call_music_video_search(input):
    input = input.replace(",", " ")
    return youtube.run(input)

def get_memory(session_id):
    # print("mem", session_id)
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

tools = [
    Tool.from_function(
        name="Music Video Search",
        description="Use when needing to find a music video. The question will include the word video. Return a link to a YouTube video.",
        func=call_music_video_search,
    ),
    Tool.from_function(
        name="Analyzing Lyrics",
        description="For when you need to find a song by its lyrics, plot, theme or what it is about.",
        func=get_lyrics,
    ),
    Tool.from_function(
        name="Song Data",
        description="Use when you need to get data such as lyrics, album, or song name.",
        func=get_song_data,
    ),
]


agent_template = '''
You are an expert in Taylor Swift songs and lyrics. 
You will be enthusiastic and refer to yourself as a Swiftie.
Use the context to answer questions. 
Only provide information relating to Taylor Swift songs, albums and lyrics.

Answer the following questions as best you can. If you don't know the answer, say you don't know. 

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
'''

agent_prompt = PromptTemplate.from_template(agent_template)

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    handle_parsing_errors=True,
    verbose=True
    )

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},)

    return response['output']

