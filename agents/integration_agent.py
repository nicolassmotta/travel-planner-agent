class IntegrationAgent:
    def __init__(self, environment):
        self.env = environment

    def run(self):
        print("\n[Agente de Integração] Montando plano de viagem...")

        voos = self.env.get("flights")
        hoteis = self.env.get("hotels")
        atividades = self.env.get("activities")

        if not voos or not hoteis:
            print("⚠️ Dados insuficientes para integrar a viagem.")
            return

        plano = {
            "voo_escolhido": voos[0],
            "hotel_escolhido": hoteis[0],
            "atividades_sugeridas": atividades,
            "preco_estimado": voos[0]["preco"] + hoteis[0]["preco_noite"] * 3
        }

        self.env.update("plan", plano)
        print("\n--- PLANO FINAL DE VIAGEM ---")
        print(f"✈️ Voo: {plano['voo_escolhido']['companhia']} - R${plano['voo_escolhido']['preco']}")
        print(f"🏨 Hotel: {plano['hotel_escolhido']['nome']} - R${plano['hotel_escolhido']['preco_noite']}/noite")
        print("🎯 Atividades:")
        for a in plano["atividades_sugeridas"]:
            print(f"  - {a}")
        print(f"💰 Preço total estimado: R${plano['preco_estimado']}")
