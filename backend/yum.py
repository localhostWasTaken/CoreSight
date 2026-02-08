from passlib.context import CryptContext

# 1. Setup the context exactly as it appears in your auth utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

# 2. Define the password
plain_password = "password123"

# 3. Generate the hash
hashed_password = pwd_context.hash(plain_password)

# 4. Output the result
print(f"Plain: {plain_password}")
print(f"Hash:  {hashed_password}")