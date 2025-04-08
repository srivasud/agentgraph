This is an interactive chatbot that engages customer to collect the symptoms related to their condition and recommend Homeopathic alternative medicines.

This uses multi-agent architecture implemented using LangGraph in Python. 
The Triage Agent engages the customer and collects informations related to the condition (symptoms) and hands off to a Recommender agent. 
The Recommender agent recommends potential remedies based on the given context and curated Homeopathic articles (prompt).
The project uses OpenAI ChatGPT-4.0 LLM. The Triage agent calls tools to invoke REST API to collect similar documents stored in the Chroma Vector DB.
