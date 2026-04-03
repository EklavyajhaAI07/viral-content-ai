import pytest
from app.agents.trend_scout import trend_scout, run_trend_scout

def test_agent_created():
    assert trend_scout.role == "Trend Scout"
    assert trend_scout.goal is not None
    print("✅ Trend Scout agent created successfully")

def test_trend_scout_run():
    result = run_trend_scout("AI productivity tools", "instagram")
    assert result["status"] == "completed"
    assert result["trends"] is not None
    assert len(result["trends"]) > 0
    print(f"✅ Trend Scout returned results for: {result['topic']}")
    print(f"Result preview: {result['trends'][:200]}...")

if __name__ == "__main__":
    test_agent_created()
    test_trend_scout_run()
