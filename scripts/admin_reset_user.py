#!/usr/bin/env python3
"""
One-off script to reset a user's password from the command line.
Usage: python scripts/admin_reset_user.py <username> <temporary_password>
Note: This script must be run from within the project virtualenv and with DB access.
"""
import sys
from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

if len(sys.argv) != 3:
    print('Usage: admin_reset_user.py <username> <temporary_password>')
    sys.exit(2)

username = sys.argv[1]
temp_pw = sys.argv[2]

s = SessionLocal()
user = s.query(User).filter(User.username == username).first()
if not user:
    print('User not found')
    sys.exit(1)
user.hashed_password = hash_password(temp_pw)
user.must_change_password = True
s.add(user)
s.commit()
print(f"Password reset for {username}. User must change password on next login.")
