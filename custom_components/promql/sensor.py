from datetime import timedelta
import logging

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)

from .const import (
    DOMAIN,
    PROMETHEUS_METRIC_KEY,
    PROMETHEUS_VALUE_KEY,
    PROMETHEUS_JOB_KEY,
    PROMETHEUS_INSTANCE_KEY,
)
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

    sensors = {}

    @callback
    def async_data_updated():
        updated_sensors = []
        for data in coordinator.data:
            unique_id = generate_unique_id(entry.entry_id, data[PROMETHEUS_METRIC_KEY])

            if unique_id in sensors:
                sensors[unique_id].setData(data)
            else:
                newSensor = PromQLSensor(entry, unique_id, data)

                sensors[unique_id] = newSensor
                async_add_entities([newSensor])

            updated_sensors.append(sensors[unique_id])

        for sensor in sensors.values():
            if sensor not in updated_sensors:
                sensor.setData(None)

    coordinator.async_add_listener(async_data_updated)

    await coordinator.async_config_entry_first_refresh()


def generate_unique_id(entry_id, metric):
    return f"{entry_id}_{'_'.join(metric.values())}"


class PromQLSensor(SensorEntity):
    def __init__(self, entry, unique_id, data):
        self._entry_id = entry.entry_id
        self._name = entry.data[CONF_NAME]
        self._attr_unit_of_measurement = entry.data.get(CONF_UNIT_OF_MEASUREMENT)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = unique_id
        self._data = data

    @property
    def name(self) -> str:
        if self._getData() is None or self._getInstanceHost() is None:
            return self._name

        return f"{self._getInstanceHost()} {self._name}"

    @property
    def state(self) -> str:
        return self._getValue()[1]

    @property
    def extra_state_attributes(self) -> dict:
        return self._getMetric()

    @property
    def device_info(self) -> DeviceInfo:
        if self._getInstance() is None:
            return None

        return DeviceInfo(
            identifiers={(DOMAIN, self._getInstance())},
            name=self._getInstanceHost(),
        )

    @property
    def should_poll(self) -> bool:
        return False

    def _getData(self) -> dict:
        return self._data

    def setData(self, data):
        if data is not None:
            self._data = data
        self._attr_available = data is not None
        self.async_write_ha_state()

    def _getMetric(self) -> dict:
        return self._getData()[PROMETHEUS_METRIC_KEY]

    def _getValue(self) -> str:
        return self._getData()[PROMETHEUS_VALUE_KEY]

    def _getJob(self) -> str:
        return self._getMetric().get(PROMETHEUS_JOB_KEY)

    def _getInstance(self) -> str:
        return self._getMetric().get(PROMETHEUS_INSTANCE_KEY)

    def _getInstanceHost(self) -> str:
        if self._getInstance() is None:
            return None
        return self._getInstance().split(":")[0]
