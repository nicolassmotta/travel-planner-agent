import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routers import auth, plan # Importa os roteadores

# Carrega variáveis
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

# Inicializa Banco de Dados
models.Base.metadata.create_all(bind=database.engine)

# Inicializa App
app = FastAPI(title="Travel Planner API", version="1.0.0")

# Configura CORS
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as Rotas
app.include_router(auth.router)
app.include_router(plan.router)

# Endpoint de saúde simples
@app.get("/health")
def health_check():
    return {"status": "ok"}