from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from google.adk.runners import Runner
from google.genai import types
import markdown_it
from weasyprint import HTML, CSS

from app import schemas, auth, models
from app.agent import booking_integrator, session_service # Importa do novo arquivo agent.py

router = APIRouter(tags=["Planning"])

async def stream_plan_response(request: schemas.TravelRequest, user_email: str) -> AsyncGenerator[str, None]:
    APP_NAME = "travel_planner"
    USER_ID = user_email
    SESSION_ID = f"session_{datetime.now().timestamp()}" 

    print(f"\n--- NOVA REQUISIÇÃO DE {user_email} ---")

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
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

# --- PDF ---
PDF_CSS = """
@page { size: A4; margin: 2cm; }
body { font-family: sans-serif; font-size: 11pt; line-height: 1.6; }
h1 { font-size: 24pt; }
h2 { font-size: 18pt; border-bottom: 1px solid #eaeaea; }
a { color: #007bff; text-decoration: none; }
"""

@router.post("/download-plan")
async def download_plan(request: schemas.PlanDownloadRequest):
    try:
        md = markdown_it.MarkdownIt()
        html_content = md.render(request.plan)
        full_html = f"<html><head><style>{PDF_CSS}</style></head><body>{html_content}</body></html>"
        pdf_bytes = HTML(string=full_html).write_pdf()
        
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=plano-de-viagem.pdf"}
        )
    except Exception as e:
        return Response(status_code=500, content=f"Erro ao gerar PDF: {e}")