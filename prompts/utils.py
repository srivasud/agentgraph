from pathlib import Path

def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).parent / f"{name}.txt"
    return prompt_path.read_text()
