"""
Comprehensive test suite for EchoSim heart failure simulation application.
Tests API endpoints, game state management, and application functionality.
"""

import pytest
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app import app
import state

# Test client for FastAPI app
client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after each test."""
    # Clean up before test
    game_store = Path("game_store.json")
    if game_store.exists():
        game_store.unlink()
    
    yield
    
    # Clean up after test
    if game_store.exists():
        game_store.unlink()


class TestRootEndpoint:
    """Test the root endpoint functionality."""
    
    def test_root_returns_correct_message(self):
        """Test that root endpoint returns expected message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"detail": "EchoSim flat-repo server running"}


class TestOpenAPIEndpoint:
    """Test OpenAPI schema endpoint."""
    
    def test_openapi_endpoint_exists(self):
        """Test that OpenAPI endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Verify it's valid JSON
        data = response.json()
        assert isinstance(data, dict)


class TestGameplayEndpoints:
    """Test gameplay-related API endpoints."""
    
    def test_record_decision_valid_input(self):
        """Test recording a valid decision."""
        response = client.post("/record_decision", params={
            "user_id": "test_user",
            "action": "echocardiography",
            "outcome": "correct",
            "confidence": "sure"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains expected fields
        assert "xp_diag" in data
        assert "xp_emp" in data
        assert "xp_sys" in data
        assert "combo" in data
        assert "coins" in data
        assert "needs_night_shift" in data
        
        # Verify correct outcome increases XP
        assert data["xp_diag"] == 2  # correct + diag action
        assert data["combo"] == 1    # correct decision
    
    def test_record_decision_incorrect_outcome(self):
        """Test recording an incorrect decision."""
        response = client.post("/record_decision", params={
            "user_id": "test_user2",
            "action": "random_action",
            "outcome": "incorrect",
            "confidence": "unsure"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify incorrect outcome behavior
        assert data["xp_sys"] == 0   # no XP for incorrect
        assert data["combo"] == 0    # combo reset
        assert data["stress"] == 30  # base 20 + 10 for incorrect
        assert data["alert_debt"] == 1  # debt increased
    
    def test_record_decision_partial_outcome(self):
        """Test recording a partial correct decision."""
        response = client.post("/record_decision", params={
            "user_id": "test_user3",
            "action": "counseling",
            "outcome": "partial",
            "confidence": "sure"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify partial outcome gives 1 XP
        assert data["xp_emp"] == 1   # partial + emp action
        assert data["combo"] == 0    # partial doesn't increase combo
    
    def test_record_decision_invalid_outcome(self):
        """Test that invalid outcome values are rejected."""
        response = client.post("/record_decision", params={
            "user_id": "test_user4",
            "action": "test_action",
            "outcome": "invalid_outcome",
            "confidence": "sure"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_record_decision_invalid_confidence(self):
        """Test that invalid confidence values are rejected."""
        response = client.post("/record_decision", params={
            "user_id": "test_user5",
            "action": "test_action",
            "outcome": "correct",
            "confidence": "invalid_confidence"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_night_shift_page(self):
        """Test night shift questions endpoint."""
        response = client.get("/night_shift_page", params={"user_id": "test_user"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "questions" in data
        assert "expiry_seconds" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) == 3
        assert data["expiry_seconds"] == 90


class TestBannerGeneration:
    """Test SVG banner generation functionality."""
    
    def test_generate_banner_svg_default(self):
        """Test banner generation with default parameters."""
        response = client.get("/generate_banner_svg")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"
        assert "no-store" in response.headers["cache-control"]
        
        # Verify it's SVG content
        content = response.text
        assert content.startswith("<svg") or "svg" in content.lower()
    
    def test_generate_banner_svg_with_params(self):
        """Test banner generation with specific parameters."""
        params = {
            "xp_diag": "10",
            "xp_sys": "15", 
            "xp_emp": "5",
            "combo": "3",
            "coins": "2",
            "focus": "85",
            "stress": "15",
            "cbw": "75",
            "pill_ace": "1",
            "pill_bb": "1",
            "device_stage": "2"
        }
        
        response = client.get("/generate_banner_svg", params=params)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"
        
        # Verify XP scaling (1 XP → 4 px, minimum 1 px)
        content = response.text
        # XP values should be scaled by 4
        assert "40" in content  # xp_diag: 10 * 4
        assert "60" in content  # xp_sys: 15 * 4
        assert "20" in content  # xp_emp: 5 * 4


class TestGameStateManagement:
    """Test game state management functionality."""
    
    def test_user_creation(self):
        """Test that new users are created with default values."""
        data = state._user("new_test_user")
        user_state = data["new_test_user"]
        
        # Verify default values
        assert user_state["xp_diag"] == 0
        assert user_state["xp_emp"] == 0
        assert user_state["xp_sys"] == 0
        assert user_state["combo"] == 0
        assert user_state["coins"] == 0
        assert user_state["focus"] == 80
        assert user_state["stress"] == 20
        assert user_state["cbw"] == 70
        assert user_state["alert_debt"] == 0
    
    def test_bucket_classification(self):
        """Test action classification into XP buckets."""
        assert state._bucket("echocardiography") == "xp_diag"
        assert state._bucket("bnp test") == "xp_diag"
        assert state._bucket("angiography") == "xp_diag"
        
        assert state._bucket("counseling") == "xp_emp"
        assert state._bucket("trust building") == "xp_emp"
        assert state._bucket("diary review") == "xp_emp"
        
        assert state._bucket("medication management") == "xp_sys"
        assert state._bucket("random action") == "xp_sys"
    
    def test_evaluate_function_correct_outcome(self):
        """Test evaluation function with correct outcome."""
        result = state.evaluate("eval_test_user", "echo", "correct", "sure")
        
        assert result["xp_diag"] == 2
        assert result["combo"] == 1
        assert result["stress"] == 15  # 20 - 5 for sure confidence
        assert result["focus"] == 82   # 80 + 2 for sure confidence
        assert result["alert_debt"] == 0
        assert result["needs_night_shift"] == False
    
    def test_evaluate_function_combo_building(self):
        """Test combo building and coin earning."""
        user_id = "combo_test_user"
        
        # Build combo to 3
        state.evaluate(user_id, "action1", "correct", "sure")
        state.evaluate(user_id, "action2", "correct", "sure")
        result = state.evaluate(user_id, "action3", "correct", "sure")
        
        assert result["combo"] == 3
        assert result["coins"] == 1  # Should earn coin at combo 3
    
    def test_evaluate_function_alert_debt(self):
        """Test alert debt and night shift trigger."""
        user_id = "debt_test_user"
        
        # Build up alert debt
        state.evaluate(user_id, "action1", "incorrect", "unsure")
        state.evaluate(user_id, "action2", "incorrect", "unsure")
        result = state.evaluate(user_id, "action3", "incorrect", "unsure")
        
        assert result["alert_debt"] == 3
        assert result["needs_night_shift"] == True
    
    def test_state_persistence(self):
        """Test that state persists across function calls."""
        user_id = "persist_test_user"
        
        # First evaluation
        state.evaluate(user_id, "echo", "correct", "sure")
        
        # Second evaluation should build on first
        result = state.evaluate(user_id, "counseling", "correct", "sure")
        
        assert result["xp_diag"] == 2  # From first evaluation
        assert result["xp_emp"] == 2   # From second evaluation
        assert result["combo"] == 2    # Combo built up


class TestStaticFiles:
    """Test static file serving."""
    
    def test_static_directory_exists(self):
        """Test that static directory is created."""
        static_dir = Path("static")
        assert static_dir.exists()
        assert static_dir.is_dir()


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_user_workflow(self):
        """Test a complete user workflow from start to night shift."""
        user_id = "integration_test_user"
        
        # Make several correct decisions
        for i in range(2):
            response = client.post("/record_decision", params={
                "user_id": user_id,
                "action": "echo",
                "outcome": "correct",
                "confidence": "sure"
            })
            assert response.status_code == 200
        
        # Make incorrect decisions to trigger night shift
        for i in range(3):
            response = client.post("/record_decision", params={
                "user_id": user_id,
                "action": "bad_action",
                "outcome": "incorrect",
                "confidence": "unsure"
            })
            assert response.status_code == 200
        
        # Final decision should trigger night shift
        final_response = client.post("/record_decision", params={
            "user_id": user_id,
            "action": "another_action",
            "outcome": "incorrect",
            "confidence": "unsure"
        })
        
        assert final_response.status_code == 200
        data = final_response.json()
        assert data["needs_night_shift"] == True
        
        # Test night shift page
        night_response = client.get("/night_shift_page", params={"user_id": user_id})
        assert night_response.status_code == 200
        night_data = night_response.json()
        assert len(night_data["questions"]) == 3
        
        # Generate banner with accumulated stats
        banner_response = client.get("/generate_banner_svg", params={
            "xp_diag": str(data["xp_diag"]),
            "combo": str(data["combo"]),
            "stress": str(data["stress"])
        })
        assert banner_response.status_code == 200
        assert banner_response.headers["content-type"] == "image/svg+xml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])