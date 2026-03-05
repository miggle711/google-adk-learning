"""
Sample file with intentional security vulnerabilities for testing bandit.
DO NOT USE THIS CODE IN PRODUCTION!
"""

import pickle
import subprocess

# B105: Hardcoded password
password = "super_secret_123"
API_KEY = "sk-1234567890abcdef"

# B301: Pickle usage (unsafe deserialization)
def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# B602: Shell injection via subprocess
def run_command(user_input):
    subprocess.call(user_input, shell=True)

# B608: SQL injection (if using raw queries)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query
