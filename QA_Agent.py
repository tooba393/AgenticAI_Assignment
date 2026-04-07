import os
import json
import requests
from openai import OpenAI

# Ensure your OPENAI_API_KEY is set in environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set your OPENAI_API_KEY in environment variables before running.")

client = OpenAI(api_key=OPENAI_API_KEY)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "tooba393/AgenticAI_Assignment"

def headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"}

def qa_agent(html_code, pr_url, marketing_data):
    try:
        # HTML review
        html_prompt = f"""
        Review this HTML landing page:

        {html_code}

        Check:
        - Matches product spec
        - Has headline
        - Features included

        Return JSON:
        {{
          "verdict": "pass/fail",
          "issues": []
        }}
        """
        html_review = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": html_prompt}],
            max_tokens=200
        )
        html_result = json.loads(html_review.choices[0].message.content)

        # Marketing review
        marketing_prompt = f"""
        Review marketing content:

        {json.dumps(marketing_data)}

        Check:
        - Tagline quality
        - Email has call to action
        - Tone appropriate

        Return JSON:
        {{
          "verdict": "pass/fail",
          "issues": []
        }}
        """
        marketing_review = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": marketing_prompt}],
            max_tokens=200
        )
        marketing_result = json.loads(marketing_review.choices[0].message.content)

        # Combine results
        final_verdict = "pass"
        issues = []

        if html_result.get("verdict") == "fail":
            final_verdict = "fail"
            issues.extend(html_result.get("issues", []))

        if marketing_result.get("verdict") == "fail":
            final_verdict = "fail"
            issues.extend(marketing_result.get("issues", []))

        # Post comments on PR
        pr_number = pr_url.split("/")[-1]
        comment_url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/comments"

        for issue in issues[:2]:
            response = requests.post(
                comment_url,
                headers=headers(),
                json={"body": f"QA Issue: {issue}"}
            )
            if response.status_code != 201:
                print(f"Failed to post comment: {response.text}")

        print("QA comments posted")
        return {"verdict": final_verdict, "issues": issues}

    except Exception as e:
        # Catch any OpenAI errors (quota, authentication, etc.)
        print(f"Error calling OpenAI API: {e}")
        return {"verdict": "error", "issues": [str(e)]}


if __name__ == "__main__":
    result = qa_agent("<html>test</html>", "https://github.com/test/pr/1", {})
    print(result)