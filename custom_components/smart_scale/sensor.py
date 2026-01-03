from homeassistant.helpers.entity import Entity

class SmartScaleSensor(Entity):
    def __init__(self, name, sensor_type):
        self._name = name
        self._state = None
        self._attributes = {}
        self._type = sensor_type

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update_data(self, data: dict):
        """Update sensor data based on type."""
        if self._type == "weight":
            self._state = data.get("weight")
            self._attributes = {
                "person": data.get("person"),
                "timestamp": data.get("timestamp"),
                "bmi": data.get("bmi"),
            }
        elif self._type == "body":
            self._state = data.get("muscle")  # Example, can map other values
            self._attributes = data
        elif self._type == "person":
            self._state = data.get("person")
            self._attributes = data
