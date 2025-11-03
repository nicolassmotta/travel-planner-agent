class ActivitiesAgent:
    def __init__(self, environment):
        self.env = environment

    def run(self, cidade, perfil):
        print("\n[Agente de Atividades] Recomendando atividades...")

        atividades = {
            "aventura": ["Passeio de barco", "Trilha na montanha", "Mergulho"],
            "romântico": ["Jantar à luz de velas", "Pôr do sol na praia", "Passeio de balão"],
            "cultural": ["Museu de Arte", "Centro Histórico", "Feira de Artesanato"]
        }

        recomendadas = atividades.get(perfil.lower(), ["Passeio pela cidade"])
        self.env.update("activities", recomendadas)
        print(f"Atividades sugeridas para perfil '{perfil}' em {cidade}:")
        for a in recomendadas:
            print(f"  - {a}")
