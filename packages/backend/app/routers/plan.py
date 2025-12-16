from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
# Tenta importar o runner, se falhar (sem SDK), evita crash total no import
try:
    from google.adk.runners import Runner
    from google.genai import types
except ImportError:
    print("AVISO: Bibliotecas Google GenAI/ADK não encontradas. O endpoint de plano falhará se chamado.")
    Runner = None
    types = None

import markdown_it

from app import schemas, auth, models
# Importa do novo arquivo agent.py que criamos para evitar erro de módulo faltando
from app.agent import booking_integrator, session_service 

router = APIRouter(tags=["Planning"])

async def stream_plan_response(request: schemas.TravelRequest, user_email: str) -> AsyncGenerator[str, None]:
    if not Runner:
        yield "ERRO: Bibliotecas de IA não instaladas no servidor."
        return

    APP_NAME = "travel_planner"
    USER_ID = user_email
    SESSION_ID = f"session_{datetime.now().timestamp()}" 

    print(f"\n--- NOVA REQUISIÇÃO DE {user_email} ---")

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    # Inicializa o Runner com o agente importado
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    final_return_date = request.returnDate if request.returnDate else request.departureDate

    user_prompt = f"""
    Planeje minha viagem com os seguintes detalhes:
    - Origem: {request.origin}
    - Destino: {request.destination}
    - Data de Ida: {request.departureDate}
    - Data de Volta: {final_return_date} 
    - Orçamento Total: R$ {request.totalBudget} 
    - Orçamento Hotel (por noite): R$ {request.nightlyBudget}
    - Preferências: {request.preferences}
    """

    content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        yield part.text
    except Exception as e:
        yield f"\n\nERRO INTERNO DO SERVIDOR: {e}"
    finally:
        # Verifica se o método close existe antes de chamar (segurança)
        if hasattr(runner, 'close'):
            await runner.close()

@router.post("/generate-plan")
async def generate_plan(
    request: schemas.TravelRequest, 
    current_user: models.User = Depends(auth.get_current_user)
):
    return StreamingResponse(
        stream_plan_response(request, current_user.email), 
        media_type="text/event-stream"
    )

@router.post("/download-plan")
async def download_plan(request: schemas.PlanDownloadRequest):
    return Response(content="PDF indisponível (Falta biblioteca GTK no servidor)", media_type="text/plain")