import secrets

# Generates a 32-byte (256-bit) random hex string (64 hex characters)
secret_key_hex = secrets.token_hex(32)
print(f"Hex Key: {secret_key_hex}")

# Generates a URL-safe text string (e.g., for tokens in URLs)
secret_key_urlsafe = secrets.token_urlsafe(32)
print(f"URL-safe Key: {secret_key_urlsafe}")

# Generates random bytes (useful for binary secrets)
secret_key_bytes = secrets.token_bytes(32)
print(f"Bytes Key: {secret_key_bytes}")
