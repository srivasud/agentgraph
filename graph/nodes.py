from agents.llm import agent
from tools.chroma_tools import get_similar_articles
from .state import TriageState
from prompts.utils import load_prompt
from pathlib import Path
import re

def route_after_symptom_question(state):
    questions = state.get("symptom_questions", [])
    answered = state.get("user_symptoms", {})

    if len(answered) < len(questions):
        return "AskNextSymptomQuestion"
    else:
        state["ready_for_prescriber"] = True
        return "PrescriberStart" 

def prompt_user(state: TriageState) -> TriageState:
    # Decide what to ask based on current state
    print(f"First time getting into prompt_user.Condition Category::..{state.get("condition_category")}")
    if not state.get("condition_category"):
        print(" Hello! How are you feeling today? What condition category of illness are you dealing with? (e.g.,Anxiety, Depression)")
    elif not state.get("clarified"):
        print(" I need to understand a few things to help you better:")
        print("   - What's your goal? (diagnosis, remedy, or just exploring?)")
        print("   - What condition category of illness are you dealing with? (e.g., Anxiety, Depression)")
        print("   - Who is this for? An adult or a child?")
    elif not state.get("target_audience_type"):
        print("Who is the subject of discussion? Self, spouse, child, father, or mother?")
    else:
        print(f"Let's talk about the symptoms experienced by {state.get("target_audience_type")}")

    user_input = input("\nYou: ")
    return {"user_input": user_input}

def extract_condition_category(state: TriageState) -> TriageState:
    input_text = state.get("input_text", "").lower()
    
    if "anxious" in input_text or "anxiety" in input_text:
        state["condition_category"] = "Anxiety"
    elif "depressed" in input_text or "depression" in input_text:
        state["condition_category"] = "Depression"
    # add more conditions as needed
    return state

def ask_symptoms(state: TriageState) -> TriageState:
    if state.get("similar_articles"):
        articles = state.get("similar_articles")
    else:
        articles = []
    prompt = f"""
    Given the following context on {state['condition_category']}:
    {articles}

    Please generate 5 to 10 relevant symptom questions based on the context provided above. Ensure that each question is clear, concise, and directly related to the condition mentioned.

    Return the questions in the following format:
    Question Text\n
    Question Text\n
    Please make sure each question appears on a **new line** with no other text or explanations.
    """ 
    llm_response = agent.run(prompt)
    state["symptom_questions"] = llm_response.split("\n")
    return state

def ask_next_symptom(state: TriageState) -> TriageState:
    questions = state.get("symptom_questions", [])
    if not questions:
        print("No symptom questions found.")
        state["symptom_collection_done"] = True
        return state

    answers = state.get("user_symptoms", [])
    answers = answers if isinstance(answers, list) else []
    index = state.get("current_symptom_index", 0)

    while index < len(questions):
        question = questions[index]
        print(f"{index + 1}: {question}")
        user_answer = input("📝 You: ").strip()
        
        if user_answer == "":
            print("Please provide an answer (or type 'no' / 'not applicable').")
            continue
        
        answers.append({
            "question": question,
            "answer": user_answer
        })
        index += 1

    state["user_symptoms"] = answers
    state["current_symptom_index"] = index
    state["symptom_collection_done"] = True
    state["clarified"] = True
    state["ready_for_prescriber"]=True
    print("Thank you. That's all the symptom questions for now.")
    return state

def extract_user_intent(state: TriageState) -> dict:
    input_text = state.get("user_input", "")
    prompt_template = load_prompt("triage_prompt")
    prompt = prompt_template.format(input=input_text)

    result = agent.run(prompt)

    intent = None
    category = None

    # Try to extract values based on known keys in the result
    lines = result.lower().splitlines()
    for line in lines:
        if "objective" in line:
            intent = line.split(":")[1].strip().capitalize()
        if "category" in line:
            category = line.split(":")[1].strip().capitalize()

    clarified = bool(intent and category)

    return {
        "objective": intent,
        "condition_category": category,
        "clarified": clarified
    }

def determine_target_relation(state: TriageState) -> TriageState:
    input_text = state.get("input_text", "").lower()

    if not state.get("target_audience_type"):
        if "child" in input_text:
            state["target_audience_type"] = "child"
        elif "wife" in input_text or "spouse" in input_text:
            state["target_audience_type"] = "spouse"
        elif "father" in input_text:
            state["target_audience_type"] = "father"
        elif "mother" in input_text:
            state["target_audience_type"] = "mother"
        else:
            state["target_audience_type"] = "self"

    return state
def determine_target_audience(state: TriageState) -> TriageState:
    type_ = state.get("target_audience_type", "self")

    if type_ == "child":
        state["target_audience"] = "Child"
    else:
        state["target_audience"] = "Adult"

    return state
def route_after_determine_audience(state: TriageState) -> str:
    return "RetrieveArticles" if state.get("target_audience_type") else "PromptUser"

def retrieve_articles(state: TriageState) -> TriageState:
    query = state.get("condition_category") or "Anxiety"
    category = "diagnosis"
    
    # Defensive fallback
    if not isinstance(query, str):
        query = str(query)
    if not isinstance(category, str):
        category = str(category)

    try:
        articles = get_similar_articles.run({"query":query, "category":category})
        if articles:
            state["similar_articles"] = articles
        else:
            state["similar_articles"]=[]
    except Exception as e:
        print(f"[RetrieveArticles] Error: {e}")
        state["similar_articles"] = []

    return state
def infer_symptoms_and_prompt(state: TriageState) -> TriageState:
    articles = state["similar_articles"]
    if isinstance(articles[0], dict) and "content" in articles[0]:
        context = "\n\n".join([a["content"] for a in articles][:2])
    else:
        context = "\n\n".join(articles[:2])
    result = agent.run(f"""
    Based on this information, what common symptoms are seen? {context}
    Ask the user if they are experiencing any of these.
    """)
    print(result)
    return state

def start_prescriber(state: dict) -> dict:
    symptoms = state.get("user_symptoms", [])
    articles = state.get("similar_articles", "")
    subject_type = state.get("target_audience", "adult").capitalize()
    relation = state.get("target_audience_type", "self").capitalize()
    condition = state.get("condition_category", "the condition")

    if not symptoms:
        state["prescriber_response"] = "I couldn't find any symptoms to base a suggestion on."
        return state

    symptom_summary = "\n".join(f"- {s}" for s in symptoms)

    prompt = f"""
        You are a homeopathy expert. Based on the following information:

        Subject: {relation} ({subject_type})
        Condition Category: {condition}
        Symptoms:
        {symptom_summary}

        Context from medical literature:
        {articles}

        Please suggest a suitable homeopathy remedy or remedies only from the provided context. Include a brief explanation for your choice. If you need more information, mention what else would be helpful to know.
        """

    response = agent.invoke(prompt)
    state["prescriber_processed"] = True
    if not response.get('output'):
        state["prescriber_response"] = "Remedy not available. Please contact our practitioners."
    else:
        state["prescriber_response"] = response.get('output')
    print(state.get("prescriber_response"))
    return state
