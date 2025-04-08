from typing import List
from langchain.tools import tool
import requests

@tool(description="Fetch similar articles for a query and category using a remote API.")
def get_similar_articles(query: str, category: str) -> List[str]:
    articles=[]
    response = requests.get(f"http://localhost:8080/practitioner/remedy_article", params={"query": query, "type":category})
    articles.extend(response.json()["documents"])
    response = requests.get(f"http://localhost:8080/practitioner/diagnosis_article", params={"query": query, "type":category})
    articles.extend(response.json()["documents"])
    return articles

homeopathy_tools = [get_similar_articles]
