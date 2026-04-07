import os
import requests

# Agar OpenAI client install hai
try:
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    openai_installed = True
except ImportError:
    openai_installed = False

def safe_llm_call(prompt, max_tokens=500):
    # 1️⃣ Try OpenAI first
    if openai_installed:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI failed: {e}\nFalling back to HuggingFace LLM...")

    # 2️⃣ Fallback: HuggingFace Inference API
    hf_api_key = os.environ.get("HF_API_KEY")
    if not hf_api_key:
        raise ValueError("HF_API_KEY environment variable not set for HuggingFace fallback.")

    headers = {"Authorization": f"Bearer {hf_api_key}"}
    json_data = {"inputs": prompt, "options": {"wait_for_model": True}}

    hf_response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers=headers,
        json=json_data
    )

    if hf_response.status_code != 200:
        raise Exception(f"HuggingFace API failed: {hf_response.text}")

    return hf_response.json()[0]["generated_text"]

# Example usage
if __name__ == "__main__":
    prompt = "Write a product spec for a platform that sells second-hand textbooks."
    output = safe_llm_call(prompt)
    print(output)