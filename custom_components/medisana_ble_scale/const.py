"""Constants for the BS440 BLE integration."""
from typing import Final

DOMAIN = "bs440_ble"

# Configuration
CONF_MAC = "mac_address"

# Time offset (from script)
TIME_OFFSET = 1262304000

# UUIDs
CHAR_PERSON = "00008a82-0000-1000-8000-00805f9b34fb"
CHAR_WEIGHT = "00008a21-0000-1000-8000-00805f9b34fb"
CHAR_BODY = "00008a22-0000-1000-8000-00805f9b34fb"
CHAR_COMMAND = "00008a81-0000-1000-8000-00805f9b34fb"

DEFAULT_NAME = "BS440 Scale"