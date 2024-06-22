from summary_actions import summarize_actions
import pytest

def test_summarize_actions_with_accident():
    # Scenario: Car accident
    text = "I see a car accident"
    expected_actions = ["ambulance", "medical"]
    summary = summarize_actions(text).lower()
    assert any(expected_action in summary for expected_action in expected_actions) 

def test_summarize_actions_with_fire():
    # Scenario: Fire outbreak
    text = "There is a fire in the building"
    expected_actions = ["fire truck", "fire department"]
    summary = summarize_actions(text).lower()
    assert any(expected_action in summary for expected_action in expected_actions) 

def test_summarize_actions_with_robbery():
    # Scenario: Robbery
    text = "A bank is being robbed"
    expected_actions = ["police", "police department"]
    summary = summarize_actions(text).lower()
    assert any(expected_action in summary for expected_action in expected_actions) 
