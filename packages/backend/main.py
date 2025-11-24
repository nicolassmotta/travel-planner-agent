# main.py
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
# Importa a nova ferramenta de imagens
from tools import flights, hotels, recommendations, weather, images
from datetime import datetime
from typing import Optional, AsyncGenerator

# Importações do FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from fastapi.responses import StreamingResponse
from fastapi.responses import Response

# Importações para PDF
import markdown_it
from weasyprint import HTML, CSS

# === CONFIGURAÇÃO INICIAL ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

today_str = datetime.now().strftime("%Y-%m-%d")

# === INSTRUÇÕES DO AGENTE (ATUALIZADO) ===
agent_instructions = f"""
Você é um Coordenador de Viagens de elite. A data de HOJE é: {today_str}.

Sua tarefa é gerar um plano de viagem completo, detalhado e VISUAL em UMA ÚNICA RESPOSTA.
Você receberá todos os dados do usuário de uma vez.

Use as ferramentas nesta ordem lógica:

1.  **VOOS:** Chame 'get_flight_options'.
2.  **HOTÉIS:** Chame 'get_hotel_options'.
3.  **ATIVIDADES:** Chame 'get_recommendations' para atividades baseadas nas preferências.
4.  **CLIMA:** Chame 'get_historical_average_weather'.
5.  **IMAGENS (IMPORTANTE):** Chame 'get_destination_images' para a cidade de destino e para as principais atrações ou hotéis sugeridos.

**Formato do Relatório Final:**
O relatório deve ser em Markdown rico.
* Use títulos claros (###).
* **INCLUA IMAGENS:** Sempre que mencionar o destino ou um ponto turístico importante e tiver uma URL de imagem, insira-a usando a sintaxe Markdown: `![Descrição](URL)`. Tente colocar uma imagem de capa bonita no início.
* Organize voos e hotéis em listas.
* Crie um roteiro dia a dia sugerido se houver tempo suficiente.
* Inclua o resumo do clima.

Seja inspirador, organizado e profissional.
"""

# === INICIALIZAÇÃO DO AGENTE ===
booking_integrator = LlmAgent(
    name="travel_planner",
    model="gemini-2.5-flash",
    description="Agente de viagens que coordena o planejamento passo a passo.",
    instruction=agent_instructions,
    tools=[
        flights.get_flight_options,
        hotels.get_hotel_options,
        recommendations.get_recommendations,
        weather.get_historical_average_weather,
        images.get_destination_images # Nova ferramenta adicionada
    ],
)

session_service = InMemorySessionService()

# === DEFINIÇÃO DA API ===
app = FastAPI()

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

class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: str
    returnDate: Optional[str] = None
    totalBudget: float
    nightlyBudget: float
    preferences: str

    @field_validator('totalBudget', 'nightlyBudget')
    def budgets_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('O orçamento não pode ser negativo')
        return v

# === STREAMING ===
async def stream_plan_response(request: TravelRequest) -> AsyncGenerator[str, None]:
    APP_NAME = "travel_planner"
    USER_ID = "user_api" 
    SESSION_ID = f"session_{datetime.now().timestamp()}" 

    print("\n--- NOVA REQUISIÇÃO (STREAM) RECEBIDA ---")
    print(f"Dados Recebidos: {request.model_dump_json(indent=2)}")

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    final_return_date = request.returnDate
    if not final_return_date:
        final_return_date = request.departureDate

    user_prompt = f"""
    Planeje minha viagem com os seguintes detalhes:
    - Origem: {request.origin}
    - Destino: {request.destination}
    - Data de Ida: {request.departureDate}
    - Data de Volta: {final_return_date} 
    - Orçamento Total: R$ {request.totalBudget} 
    - Orçamento Hotel (por noite): R$ {request.nightlyBudget}
    - Preferências: {request.preferences}
    
    Lembre-se de buscar imagens para ilustrar o roteiro!
    """

    print("\n--- PROMPT ENVIADO AO AGENTE ---")
    print(user_prompt)

    content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        # Opcional: printar apenas pedaços grandes para não poluir o log
                        if len(part.text) > 5:
                            print(f"--- STREAM CHUNK: {part.text[:50]}... ---")
                        yield part.text
    
    except Exception as e:
        print(f"!!!!!!!!!! ERRO NO AGENTE !!!!!!!!!!")
        print(f"Erro ao processar agente: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        yield f"\n\nERRO INTERNO DO SERVIDOR: {e}"
    finally:
        await runner.close()
        print("--- STREAM CONCLUÍDA ---")


@app.post("/generate-plan")
async def generate_plan(request: TravelRequest):
    return StreamingResponse(stream_plan_response(request), media_type="text/event-stream")

# === CSS PROFISSIONAL PARA PDF ===
PDF_CSS = """
@page { 
    size: A4; 
    margin: 2.5cm; 
    @bottom-center {
        content: "Travel Planner AI • Página " counter(page);
        font-size: 9pt;
        color: #666;
    }
}
body { 
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; 
    font-size: 11pt; 
    line-height: 1.6; 
    color: #333;
}
h1 { 
    font-size: 26pt; 
    color: #2c3e50; 
    text-align: center; 
    margin-bottom: 1em;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}
h2 { 
    font-size: 18pt; 
    color: #2980b9; 
    margin-top: 1.5em;
    border-bottom: 1px solid #eee; 
    padding-bottom: 5px; 
}
h3 { 
    font-size: 14pt; 
    color: #16a085;
    margin-top: 1.2em;
}
p { margin-bottom: 0.8em; text-align: justify; }
ul, ol { 
    padding-left: 1.5em; 
    margin-bottom: 1em; 
}
li { margin-bottom: 0.4em; }
a { color: #3498db; text-decoration: none; }
strong { color: #2c3e50; }
/* Estilo para imagens no PDF */
img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 1em 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
/* Destacar caixas de informação */
blockquote {
    background: #f9f9f9;
    border-left: 5px solid #3498db;
    margin: 1.5em 10px;
    padding: 0.5em 10px;
}
"""

class PlanDownloadRequest(BaseModel):
    plan: str

@app.post("/download-plan")
async def download_plan(request: PlanDownloadRequest):
    try:
        # Converte a string Markdown para HTML
        md = markdown_it.MarkdownIt()
        html_content = md.render(request.plan)
        
        # Junta o HTML com o CSS aprimorado
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{PDF_CSS}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Gera o PDF em memória
        pdf_bytes = HTML(string=full_html).write_pdf()
        
        # Devolve o ficheiro PDF
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=plano-de-viagem.pdf"}
        )
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return Response(status_code=500, content=f"Erro ao gerar PDF: {e}")