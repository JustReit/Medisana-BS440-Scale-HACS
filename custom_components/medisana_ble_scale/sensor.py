from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfMass, PERCENTAGE, UnitOfEnergy
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from .const import DOMAIN

SENSORS = [
    ("weight", "Weight", UnitOfMass.KILOGRAMS, "mdi:scale-bathroom", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT),
    ("bmi", "BMI", "", "mdi:human-pregnant", None, SensorStateClass.MEASUREMENT),
    ("fat", "Body Fat", PERCENTAGE, "mdi:human", None, SensorStateClass.MEASUREMENT),
    ("tbw", "Body Water", PERCENTAGE, "mdi:water-percent", None, SensorStateClass.MEASUREMENT),
    ("muscle", "Muscle Mass", PERCENTAGE, "mdi:arm-flex", None, SensorStateClass.MEASUREMENT),
    ("bone", "Bone Mass", UnitOfMass.KILOGRAMS, "mdi:bone", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT),
    ("kcal", "Calories", UnitOfEnergy.KILO_CALORIE, "mdi:fire", None, SensorStateClass.MEASUREMENT),
    ("last_measurement", "Last Measurement", None, "mdi:clock-outline", SensorDeviceClass.TIMESTAMP, None),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    known_users = set()

    def add_user_entities():
        new_entities = []
        for person_id in list(coordinator.data.keys()):
            if person_id not in known_users:
                for key, name, unit, icon, dev_class, state_class in SENSORS:
                    if person_id == 255 and key != "weight":
                        continue
                    new_entities.append(BS440UserSensor(coordinator, person_id, key, name, unit, icon, dev_class, state_class))
                known_users.add(person_id)
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(add_user_entities))
    add_user_entities()

class BS440UserSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, person_id, key, name, unit, icon, dev_class, state_class):
        super().__init__(coordinator)
        self.person_id = person_id
        self._key = key

        user_label = coordinator.user_names.get(person_id)
        if not user_label:
            user_label = "Guest" if person_id == 255 else f"User {person_id}"

        self._attr_name = f"{user_label} {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = dev_class
        self._attr_state_class = state_class
        self._attr_unique_id = f"{coordinator.mac}_user_{person_id}_{key}"

    @property
    def native_value(self):
        user_data = self.coordinator.data.get(self.person_id, {})
        val = user_data.get(self._key)

        if self._key == "last_measurement" and val:
            return dt_util.utc_from_timestamp(val)
        return val

    @property
    def device_info(self):
        user_label = self.coordinator.user_names.get(self.person_id) or (f"User {self.person_id}")
        return {
            "identifiers": {(DOMAIN, f"{self.coordinator.mac}_user_{self.person_id}")},
            "name": f"BS440 {user_label}",
            "manufacturer": "Medisana",
            "model": "BS440 / BS444",
        }