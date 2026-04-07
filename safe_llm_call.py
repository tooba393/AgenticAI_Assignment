import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_KEY = os.environ.get("HF_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Optional OpenAI import
try:
    from openai import OpenAI
    openai_installed = True
except ImportError:
    openai_installed = False

# Optional local HuggingFace model
try:
    from transformers import pipeline
    import torch
    local_model_available = True
except ImportError:
    local_model_available = False

# Initialize local model once
_local_pipeline = None
if local_model_available:
    try:
        _local_pipeline = pipeline("text-generation", model="gpt2", device=0 if torch.cuda.is_available() else -1)
        print("Local GPT2 model loaded successfully.")
    except Exception as e:
        print(f"Local model failed to load: {e}")
        _local_pipeline = None

def safe_llm_call(prompt, max_tokens=500):
    # 1️⃣ Try OpenAI first
    if openai_installed and OPENAI_KEY:
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            print("Used OpenAI API ✅")
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI failed: {e}\nFalling back to HuggingFace...")

    # 2️⃣ HuggingFace API fallback
    if HF_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_KEY}"}
            json_data = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
            hf_url = "https://router.huggingface.co/api/models/tiiuae/falcon-7b-instruct"
            hf_resp = requests.post(hf_url, headers=headers, json=json_data)

            if hf_resp.status_code == 200:
                data = hf_resp.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    print("Used HuggingFace API ✅")
                    return data[0]["generated_text"]
                elif isinstance(data, dict) and "generated_text" in data:
                    print("Used HuggingFace API ✅")
                    return data["generated_text"]
                else:
                    print(f"Unexpected HuggingFace response: {data}")
            else:
                print(f"HuggingFace API failed: {hf_resp.status_code} - {hf_resp.text}")
        except Exception as e:
            print(f"HuggingFace API call error: {e}")

    # 3️⃣ Local model fallback
    if _local_pipeline:
        try:
            result = _local_pipeline(prompt, max_new_tokens=max_tokens, do_sample=True)
            print("Used Local GPT2 model ✅")
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
            else:
                return str(result)
        except Exception as e:
            print(f"Local model failed: {e}")

    raise Exception("All LLM calls failed. Please check API keys or install transformers locally.")