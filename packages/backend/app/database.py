import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Garante que as variáveis de ambiente sejam carregadas
load_dotenv()

# Pega a URL do arquivo .env. Se não existir, usa SQLite como fallback (segurança)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel.db")

# Configuração do Engine
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    # Configuração específica para SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Configuração para PostgreSQL (e outros bancos reais)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()