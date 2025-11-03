class TravelEnvironment:
    """
    Ambiente central onde os agentes compartilham informações.
    Similar ao modelo usado no LABRIOT.
    """

    def __init__(self):
        self.data = {
            "flights": None,
            "hotels": None,
            "activities": None,
            "plan": None
        }

    def update(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)
