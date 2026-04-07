import os, requests
from dotenv import load_dotenv

load_dotenv()
HF_KEY = os.environ.get("HF_API_KEY")
prompt = "Hello world, write a short poem."

headers = {"Authorization": f"Bearer {HF_KEY}"}
hf_url = "https://router.huggingface.co/api/models/tiiuae/falcon-7b-instruct"

resp = requests.post(hf_url, headers=headers, json={"inputs": prompt})
print(resp.status_code, resp.text)