from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)

from .const import DOMAIN
from . import requestData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    async def async_update_data():
        result = await hass.async_add_executor_job(
            requestData,
            entry.data,
        )
        return result["data"]["result"]

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=15),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        MyEntity(coordinator, entry, idx) for idx, ent in enumerate(coordinator.data)
    )


class MyEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, idx):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._idx = idx
        self._name = entry.data[CONF_NAME]
        self._attr_unit_of_measurement = entry.data.get(CONF_UNIT_OF_MEASUREMENT)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_{self._idx}"

    @property
    def name(self) -> str:
        return f"{self._getInstanceHost()} {self._name}"

    @property
    def state(self) -> str:
        return self._getValue()[1]

    @property
    def extra_state_attributes(self) -> dict:
        return self._getMetric()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._getInstance())},
            name=self._getInstanceHost(),
        )

    def _getData(self) -> dict:
        return self.coordinator.data[self._idx]

    def _getMetric(self) -> dict:
        return self._getData()["metric"]

    def _getValue(self) -> str:
        return self._getData()["value"]

    def _getInstance(self) -> str:
        return self._getMetric()["instance"]

    def _getInstanceHost(self) -> str:
        return self._getInstance().split(":")[0]
