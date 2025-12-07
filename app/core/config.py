import os

# SQLite database in data/ folder (works for both local and Docker)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/dev.db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
