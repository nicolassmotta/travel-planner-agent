class HotelAgent:
    def __init__(self, environment):
        self.env = environment

    def run(self, cidade, orcamento):
        print("\n[Agente de Hospedagem] Buscando hotéis...")

        hoteis = [
            {"nome": "Hotel Central", "preco_noite": 400, "avaliacao": 8.9},
            {"nome": "Pousada Sol", "preco_noite": 300, "avaliacao": 8.2},
            {"nome": "Eco Hostel", "preco_noite": 150, "avaliacao": 7.5}
        ]

        # Seleciona os hotéis que cabem no orçamento (3 diárias)
        viaveis = [h for h in hoteis if h["preco_noite"] * 3 <= orcamento]

        self.env.update("hotels", viaveis)
        print(f"Hotéis encontrados em {cidade}:")
        for hotel in viaveis:
            print(f"  - {hotel['nome']} | R${hotel['preco_noite']}/noite | Avaliação: {hotel['avaliacao']}")
