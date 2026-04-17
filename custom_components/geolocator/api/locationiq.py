import time
import logging
import aiohttp

from .base import GeoLocatorAPI

_LOGGER = logging.getLogger(__name__)

GEOCODE_URL = "https://us1.locationiq.com/v1/reverse"
TIMEZONE_URL = "https://us1.locationiq.com/v1/timezone"


class LocationIQAPI(GeoLocatorAPI):
    """LocationIQ reverse geocoding and timezone API."""

    def __init__(self, api_key, language="en"):
        self.api_key = api_key
        self.language = language

    async def reverse_geocode(self, lat, lon, language="en"):
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1,
                "normalizeaddress": 1,
                "normalizecity": 1,
                "accept-language": language or self.language,
            }
            async with session.get(GEOCODE_URL, params=params) as resp:
                data = await resp.json()
                _LOGGER.debug("LocationIQ Reverse Geocode response: %s", data)
                return data

    async def get_timezone(self, lat, lon, language="en"):
        timestamp = int(time.time())
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "lat": lat,
                "lon": lon,
                "timestamp": timestamp,
            }
            async with session.get(TIMEZONE_URL, params=params) as resp:
                data = await resp.json()
                _LOGGER.debug("LocationIQ Timezone API response: %s", data)
                return data.get("timezone", {}).get("name")

    def format_full_address(self, data):
        """Return a formatted full address string from the geocode response."""
        addr = data.get("address", {})
        if not addr:
            return data.get("display_name", "")

        parts = []
        house_number = addr.get("house_number", "")
        road = addr.get("road", "")
        if house_number and road:
            parts.append(f"{house_number} {road}")
        elif road:
            parts.append(road)

        city = addr.get("city", "")
        state = addr.get("state", "")
        postcode = addr.get("postcode", "")
        country = addr.get("country", "")

        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if postcode:
            parts.append(postcode)
        if country:
            parts.append(country)

        return ", ".join(parts) if parts else data.get("display_name", "")

    def extract_neighborhood(self, data):
        return data.get("address", {}).get("neighbourhood")

    def extract_city(self, data):
        return data.get("address", {}).get("city")

    def extract_state_long(self, data):
        return data.get("address", {}).get("state")

    def extract_country(self, data):
        return data.get("address", {}).get("country")
