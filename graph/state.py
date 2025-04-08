from typing import Annotated
from typing import TypedDict, Dict,List, Optional

class TriageState(TypedDict):
    user_id: Optional[str]
    objective: Optional[str]
    condition_category: Optional[str]
    target_audience: Optional[str]
    target_audience_type: None
    symptom_questions: List[str]
    user_symptoms: List[Dict[str, str]]
    constraints: Optional[str]
    similar_articles: List[dict]
    user_input: Optional[str]
    clarified: bool
    ready_for_prescriber: bool
    prescriber_response: Optional[str]
    prescriber_processed: bool
