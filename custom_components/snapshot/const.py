from homeassistant.const import Platform

DOMAIN = "snapshot"

PLATFORM: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA
]

STORAGE_VERSION = 1

STORAGE_KEY = "SNAPSHOT"

