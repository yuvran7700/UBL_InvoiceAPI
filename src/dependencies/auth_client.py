"""
src.dependencies.auth_client
=================================
Purpose: Allows API calls to PropelAuth to manually manage users and organizations.
"""
from propelauth_py import init_base_auth

auth_client = init_base_auth(
    "https://39356306333.propelauthtest.com",  # Your AUTH_URL
    "28a55c0641fe65f80561bd6a5d9cdeb0481c595dd1d94079dc06e18dd1d4fed17d927df8f4ec55942a79f9b44e18fb39"  # Your API Key
)