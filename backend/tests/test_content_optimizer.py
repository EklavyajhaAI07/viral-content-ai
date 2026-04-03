from app.agents.content_optimizer import content_optimizer, run_content_optimizer

def test_agent_created():
    assert content_optimizer.role == "Content Optimizer"
    print("✅ Content Optimizer agent created successfully")

if __name__ == "__main__":
    test_agent_created()
