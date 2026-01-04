from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfMass, PERCENTAGE, UnitOfEnergy
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

SENSORS = [
    ("weight", "Weight", UnitOfMass.KILOGRAMS, "mdi:scale-bathroom", SensorDeviceClass.WEIGHT),
    ("bmi", "BMI", "", "mdi:human-pregnant", None),
    ("fat", "Body Fat", PERCENTAGE, "mdi:human", None),
    ("tbw", "Body Water", PERCENTAGE, "mdi:water-percent", None),
    ("muscle", "Muscle Mass", PERCENTAGE, "mdi:arm-flex", None),
    ("bone", "Bone Mass", UnitOfMass.KILOGRAMS, "mdi:bone", SensorDeviceClass.WEIGHT),
    ("kcal", "Calories", UnitOfEnergy.KILO_CALORIE, "mdi:fire", None),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    known_users = set()

    def add_user_entities():
        new_entities = []
        for person_id in list(coordinator.data.keys()):
            if person_id not in known_users:
                for key, name, unit, icon, dev_class in SENSORS:
                    if person_id == 255 and key != "weight":
                        continue
                    new_entities.append(BS440UserSensor(coordinator, person_id, key, name, unit, icon, dev_class))
                known_users.add(person_id)
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(add_user_entities))
    add_user_entities()

class BS440UserSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, person_id, key, name, unit, icon, dev_class):
        super().__init__(coordinator)
        self.person_id = person_id
        self._key = key
        self._attr_name = f"{name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = dev_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.mac}_user_{person_id}_{key}"

    @property
    def device_info(self):
        user_label = "Guest" if self.person_id == 255 else f"User {self.person_id}"
        return {
            "identifiers": {(DOMAIN, f"{self.coordinator.mac}_user_{self.person_id}")},
            "name": f"BS440 {user_label}",
            "manufacturer": "Medisana",
            "model": "BS440 / BS444",
        }

    @property
    def native_value(self):
        user_data = self.coordinator.data.get(self.person_id, {})
        return user_data.get(self._key)
