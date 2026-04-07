import json
from safe_llm_call import safe_llm_call

def product_agent(task_json):
    task = task_json.get("task", "Default Task")
    focus = task_json.get("focus", "")

    prompt = f"""
    Create a product specification JSON.

    Task: {task}
    Focus: {focus}

    Output JSON must include:
    - value_proposition
    - personas (name, role, pain_point)
    - features (name, description, priority)
    - user_stories (3)
    """

    spec_text = safe_llm_call(prompt)

    try:
        spec = json.loads(spec_text)
    except:
        spec = {"value_proposition": "Default", "features": [], "personas": [], "user_stories": []}

    with open("product_spec.json", "w") as f:
        json.dump(spec, f, indent=2)

    print("✅ Product Spec ready for Engineer + Marketing")
    return spec

def process_messages():
    # Placeholder for message bus integration
    pass

# ---- TEST ----
if __name__ == "__main__":
    test_input = {"task": "AI study assistant", "focus": "students productivity"}
    product_agent(test_input)