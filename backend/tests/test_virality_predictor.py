from app.agents.virality_predictor import virality_predictor, run_virality_predictor

def test_agent_created():
    assert virality_predictor.role == "Virality Scoring AI"
    print("✅ Virality Predictor agent created successfully")

if __name__ == "__main__":
    test_agent_created()
