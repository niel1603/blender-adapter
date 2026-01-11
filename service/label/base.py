class AddonService:
    def enable(self):
        pass

    def disable(self):
        pass

class ServiceRegistry:
    def __init__(self):
        self._services = []

    def add(self, service: AddonService):
        self._services.append(service)

    def enable_all(self):
        for s in self._services:
            s.enable()

    def disable_all(self):
        for s in reversed(self._services):
            s.disable()