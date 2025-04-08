import os
import json
from graph.triage_graph import build_triage_graph
from graph.state import TriageState

# --- Memory Utils ---
MEMORY_DIR = "memory"

def get_memory_path(user_id: str, target_type: str):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{user_id}_{target_type}.json")

def load_state(user_id: str, target_type: str) -> TriageState:
    path = get_memory_path(user_id, target_type)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {
            "objective": None,
            "condition_category": None,
            "target_audience": None,  # Adult/Child
            "target_audience_type": None,  # self/spouse/child/father/mother
            "user_symptoms": [],
            "constraints": None,
            "similar_articles": [],
            "user_input": None,
            "clarified": False,
        }

def save_state(state: TriageState, user_id: str, target_type: str):
    path = get_memory_path(user_id, target_type)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

# --- Main Driver ---
def main():
    # Get user ID
    user_id = input("Enter your user_id: ").strip()
    while not user_id:
        user_id = input("Enter your user_id: ").strip()

    # Load existing state if available
    subject = ""
    while not subject:
        subject = input("Who are we talking about? (self, spouse, child, father, mother): ").strip().lower()

    state = load_state(user_id, subject)

    # Greet and confirm prior session info
    if state:
        print(f"\n👋 Welcome back, {user_id}!")
        previous_subject = state.get("target_audience_type", subject)
        previous_category = state.get("condition_category")

        print(f"Last time, we were discussing {previous_subject.title()} with condition category: {previous_category or 'Unknown'}.")

        continue_session = input("Would you like to continue with the same subject and condition? (yes/no): ").strip().lower()
        if continue_session != "yes":
            state = {}  # Clear previous state

    # Collect subject type if needed
    subject_type = state.get("target_audience", "")
    while not subject_type:
        subject_type = input("Is the subject an Adult or Child? ").strip().title()

    category = state.get("condition_category")
    while not category:
        category = input("What's the category of illness we are talking about ? Example : Anxiety, Depression").strip().title()

    # Set initial state fields
    state["user_id"] = user_id
    state["target_audience_type"] = subject
    state["target_audience"] = subject_type
    state["condition_category"]=category

    triage_graph = build_triage_graph()

    # Loop for clarification phase
    #while not state.get("symptom_collection_done", False):
    #    user_input = input("📝 c You: ").strip()
    #    state["input_text"] = user_input
    #    state = triage_graph.invoke(state)
    #    state.pop("input_text", None)
    #    save_state(state, user_id, subject)

    # Continue rest of graph after clarification
    state = triage_graph.invoke(state)
    save_state(state, user_id, subject)

    print("✅ Final State:\n", json.dumps(state, indent=2))
if __name__ == "__main__":
    main()

