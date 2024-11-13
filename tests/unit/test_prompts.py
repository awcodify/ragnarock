from src.templates.prompts import PromptGenerator


def test_generate_analysis_prompt():
    current = {"cpu_usage": 0.8}
    historical = {"cpu_usage": 0.7}
    query = "analyze cpu usage"

    prompt = PromptGenerator.generate_analysis_prompt(
        current_metrics=current, historical_metrics=historical, query=query
    )

    assert "Current Metrics" in prompt
    assert "Historical Similar Patterns" in prompt
    assert "cpu_usage" in prompt
    assert query in prompt
