import os
import json
import requests
from openai import OpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

client = OpenAI()
from dotenv import load_dotenv
import os

# Environment variables load karna
load_dotenv()

hf_key = os.environ.get("HF_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
def marketing_agent(spec, pr_url):

    prompt = f"""
    Create marketing content for this product:

    {json.dumps(spec)}

    Return JSON with:
    tagline, description, email_subject, email_body,
    twitter, linkedin, instagram
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    data = json.loads(response.choices[0].message.content)

    # Send Email
    try:
        message = Mail(
            from_email=os.environ["FROM_EMAIL"],
            to_emails=os.environ["TEST_EMAIL"],
            subject=data["email_subject"],
            html_content=f"<p>{data['email_body']}</p>"
        )

        sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        sg.send(message)
        print("Email sent")

    except Exception as e:
        print("Email error:", e)

    # Send Slack Message
    slack_payload = {
        "channel": "#launches",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": data["tagline"]}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": data["description"]}
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*GitHub PR:* <{pr_url}|View PR>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Status:* Ready"
                    }
                ]
            }
        ]
    }

    try:
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
            json=slack_payload
        )
        print("Slack message sent")

    except Exception as e:
        print("Slack error:", e)

    return data


if __name__ == "__main__":
    with open("product_spec.json") as f:
        spec = json.load(f)

    marketing_agent(spec, "https://github.com/test/pr")