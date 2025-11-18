import bcrypt

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    # Generate a salt and hash the password
    # bcrypt.gensalt() generates a new salt for each hash
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored hash."""
    # Check if the plain password matches the hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
