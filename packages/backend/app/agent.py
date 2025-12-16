# Este arquivo serve para garantir que o 'import app.agent' funcione.
# Em um cenário real, aqui estaria a definição do seu Agente GenAI.

class MockSessionService:
    """Mock para simular o serviço de sessão."""
    async def create_session(self, app_name, user_id, session_id):
        print(f"[MOCK] Sessão criada: {session_id} para {user_id}")

class MockAgent:
    """Mock para simular o objeto booking_integrator."""
    def __init__(self):
        self.name = "TravelAgentMock"
        self.model = "gemini-pro"

# Instâncias exportadas que o plan.py espera encontrar
session_service = MockSessionService()
booking_integrator = MockAgent()