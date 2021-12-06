"""The promql component."""
from __future__ import annotations

import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant import exceptions
from homeassistant.const import (
    CONF_HOST,
    CONF_VERIFY_SSL,
)

from .const import (
    DOMAIN,
    PROMETHEUS_API_PATH,
    CONF_QUERY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    if not entry.data[CONF_VERIFY_SSL]:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    hass.config_entries.async_setup_platforms(entry, ["sensor"])

    entry.async_on_unload(entry.add_update_listener(async_options_updated))

    return True


async def async_options_updated(hass, entry):
    return True


async def async_unload_entry(hass, entry):
    return True


def requestData(data):
    url = f"{data[CONF_HOST]}{PROMETHEUS_API_PATH}"

    try:
        response = requests.get(
            url, params={"query": data[CONF_QUERY]}, verify=data[CONF_VERIFY_SSL]
        )
    except requests.exceptions.RequestException:
        raise ConnectionError

    if response:
        result = response.json()
        if result["status"] != "success":
            raise Exception
        if len(result["data"]["result"]) == 0:
            raise InvalidQuery

        return result


class ConnectionError(exceptions.HomeAssistantError):
    """Error to indicate that the connection to the host failed."""


class InvalidQuery(exceptions.HomeAssistantError):
    """Error to indicate that the provided query is invalid."""
