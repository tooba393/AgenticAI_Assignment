from CEO_Agent import CEOAgent
from Product_Agent import product_agent, process_messages
from Engineer_Agent import run_engineer
from Message_Bus import message_bus

def main():
    # 1️⃣ Initialize agents
    ceo = CEOAgent(message_bus)
    product_spec = product_agent(message_bus)
    engineer = run_engineer()

    # 2️⃣ CEO idea
    startup_idea = "A platform where students sell second-hand textbooks."
    ceo.receive_idea(startup_idea)

    # 3️⃣ Process messages
    for _ in range(10):
        process_messages()
        engineer.process_messages()
        ceo.process_messages()

if __name__ == "__main__":
    main()