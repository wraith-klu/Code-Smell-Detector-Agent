import os
from dotenv import load_dotenv
from openai import OpenAI
from ast_analyzer import analyze_ast

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# Dummy ML Model Prediction
def predict_code_smell(code):
    """
    Dummy ML model prediction.
    """
    return {"smell_type": "Clean", "confidence": 0.76, "all_probs": {"Clean": 0.76, "Smelly": 0.24}}


# Extract Python code from LLM response
def extract_optimized_code(full_text: str):
    if "```python" in full_text:
        try:
            return full_text.split("```python")[1].split("```")[0].strip()
        except:
            return "No code block found."
    elif "Optimized code" in full_text:
        return full_text.split("Optimized code")[-1].strip()
    return "No optimized code found in response."


# Main Agent Logic
def analyze_user_query(user_query: str, code: str) -> dict:
    # AST Analysis
    ast_findings = analyze_ast(code)
    ast_output = ast_findings if ast_findings else ["✅ No AST-level issues found"]

    # ML Prediction
    model_prediction = predict_code_smell(code)

    # LLM Analysis
    try:
        completion = client.chat.completions.create(
            model="openrouter/polaris-alpha",
            messages=[
                {"role": "system",
                 "content": "You are a Python code quality and optimization expert. Always provide optimized code in ```python ... ``` format."},
                {"role": "user",
                 "content": f"""
User Question: {user_query}

Code:
{code}

AST Results:
{ast_output}

ML Prediction:
{model_prediction}

Rules:
- If user asks about smells → explain smells
- If user asks about improvement → provide optimized code
- Keep answers structured
"""}
            ]
        )
        llm_response = completion.choices[0].message.content.strip()
    except Exception as e:
        llm_response = f"⚠️ LLM failed: {e}"

    return {
        "llm_analysis": {
            "ast_findings": ast_output,
            "model_prediction": model_prediction,
            "llm_response": llm_response
        },
        "optimized_code": extract_optimized_code(llm_response),
        "session_id": "dummy_session_1"
    }
