from langgraph.graph import StateGraph, END
from .state import TriageState
from .nodes import (
    prompt_user,
    extract_condition_category,
    determine_target_relation,
    determine_target_audience,
    route_after_determine_audience,
    retrieve_articles,
    ask_symptoms,
    ask_next_symptom,
    start_prescriber,
    route_after_symptom_question
)
import os
import uuid
import requests
from dotenv import load_dotenv
    
# Load environment variables
load_dotenv()

def route_after_extract(state: TriageState) -> str:
    return "PromptUser" if not state.get("clarified", False) else "InferSymptoms"

def build_triage_graph():
    builder = StateGraph(TriageState)

    # Define all nodes
    builder.add_node("PromptUser", prompt_user)
    builder.add_node("ExtractCondition", extract_condition_category)
    builder.add_node("DetermineTargetRelation", determine_target_relation)
    builder.add_node("DetermineTargetAudience", determine_target_audience)
    builder.add_node("RetrieveArticles", retrieve_articles)
    builder.add_node("ExtractSymptomQuestions", ask_symptoms)
    builder.add_node("AskNextSymptomQuestion", ask_next_symptom)
    builder.add_node("PrescriberStart",start_prescriber)

    # Start flow
    builder.set_entry_point("PromptUser")

    # Sequential steps to collect initial inputs
    builder.add_edge("PromptUser", "ExtractCondition")
    builder.add_edge("ExtractCondition", "DetermineTargetRelation")
    builder.add_edge("DetermineTargetRelation", "DetermineTargetAudience")

    # After determining the subject, route appropriately
    builder.add_conditional_edges(
        "DetermineTargetAudience",
        route_after_determine_audience
    )

    # After fetching relevant articles
    builder.add_edge("RetrieveArticles", "ExtractSymptomQuestions")
    builder.add_edge("ExtractSymptomQuestions", "AskNextSymptomQuestion")

    # Symptom question loop
    builder.add_conditional_edges(
        "AskNextSymptomQuestion",
        route_after_symptom_question  # returns either "AskNextSymptomQuestion" or END
    )
    builder.add_conditional_edges(
        "PrescriberStart", 
        lambda state: END if state.get("prescriber_processed") else "AskNextSymptomQuestion"
    )

    return builder.compile()
