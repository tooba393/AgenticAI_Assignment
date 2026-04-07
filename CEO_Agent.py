from safe_llm_call import safe_llm_call

class CEOAgent:
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.inbox = []

    # CEO ko idea receive karne ke liye
    def receive_idea(self, idea):
        print(f"[CEO] Received startup idea: {idea}")
        # CEO idea ko process karke product agent ko bhejta hai
        task_prompt = f"You are a CEO. Generate a clear product specification from this idea:\n{idea}"
        product_spec = safe_llm_call(task_prompt)
        # message bus me Product agent ke inbox me append karo
        self.message_bus["product"].append({
            "from": "ceo",
            "content": product_spec
        })
        print(f"[CEO] Sent product spec to Product agent.\n")

    # CEO ke messages process karne ke liye
    def process_messages(self):
        inbox = self.message_bus["ceo"]
        while inbox:
            msg = inbox.pop(0)
            print(f"[CEO] Processing message from {msg['from']}: {msg['content']}")
            # CEO feedback generate kar sakta hai
            feedback_prompt = f"You are a CEO. Give short feedback on:\n{msg['content']}"
            feedback = safe_llm_call(feedback_prompt)
            # Agar engineer ya product agent ke liye response ho to send karna
            if msg["from"] == "engineer":
                self.message_bus["engineer"].append({
                    "from": "ceo",
                    "content": feedback
                })
            elif msg["from"] == "product":
                self.message_bus["product"].append({
                    "from": "ceo",
                    "content": feedback
                })
            print(f"[CEO] Sent feedback: {feedback}\n")