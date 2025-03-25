import pytest
from fastapi import Header, HTTPException
from unittest.mock import patch
from src.services.auth_service import get_current_user_id

@pytest.mark.asyncio
@patch("src.services.auth_service.decode_token")
@patch("src.services.auth_service.session_validation")

async def test_get_current_user_id_valid(mock_session_validation, mock_decode_token):
    # Arrange: Mock a decoded token payload
    mock_decode_token.return_value = {
        "user_id": "abc-123",
        "email": "testuser@example.com",
        "exp": 9999999999  # Valid future expiry
    }

    # Mock Authorization header
    token = "Bearer MOCK.JWT.TOKEN"

    # Act
    user_id = await get_current_user_id(Authorization=token)

    # Assert
    assert user_id == "abc-123"
    mock_decode_token.assert_called_once()
    mock_session_validation.assert_called_once()

@pytest.mark.asyncio
@patch("src.services.auth_service.decode_token")
async def test_get_current_user_id_invalid_token(mock_decode_token):
    # Arrange: Simulate token decoding failure
    mock_decode_token.side_effect = Exception("Invalid Token")

    token = "Bearer INVALID.TOKEN"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_id(Authorization=token)
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in str(exc_info.value.detail)
