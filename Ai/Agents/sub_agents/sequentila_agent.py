from google.adk.agents import LlmAgent, SequentialAgent
from sub_agents.summary_agent import summary_agent
from sub_agents.search_agent import search_agent
from sub_agents.rag_agent import rag_agent

pipeline = SequentialAgent(name="motashabihat_summary_agent", sub_agents=[rag_agent, summary_agent, search_agent])
