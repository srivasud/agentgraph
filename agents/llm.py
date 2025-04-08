from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.chroma_tools import homeopathy_tools
import os
import uuid
import requests
from dotenv import load_dotenv
    
# Load environment variables
load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4")

agent = initialize_agent(
    tools=homeopathy_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)
