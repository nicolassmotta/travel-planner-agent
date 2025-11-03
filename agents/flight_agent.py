class FlightAgent:
    def __init__(self, environment):
        self.env = environment

    def run(self, origem, destino, data):
        print("\n[Agente de Voos] Buscando voos...")

        # Simula busca de voos com base nos parâmetros
        voos = [
            {"companhia": "LATAM", "preco": 950, "horario": "10:00"},
            {"companhia": "Azul", "preco": 1020, "horario": "14:30"},
            {"companhia": "Gol", "preco": 890, "horario": "06:45"},
        ]

        # Filtra por preço (pode ser adaptado)
        melhores_voos = sorted(voos, key=lambda v: v["preco"])[:2]

        self.env.update("flights", melhores_voos)
        print(f"Voos encontrados de {origem} para {destino} em {data}:")
        for voo in melhores_voos:
            print(f"  - {voo['companhia']} | R${voo['preco']} | {voo['horario']}")
