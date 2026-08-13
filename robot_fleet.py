"""
CSP221A - Fleet Management System
A small object-oriented simulation of a robot fleet.
"""

from __future__ import annotations

import abc
import functools
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class InsufficientBatteryError(Exception):
    """Raised when a robot doesn't have enough battery to perform a task."""

    def __init__(self, name: str, required: float, available: float):
        self.name = name
        self.required = required
        self.available = available
        message = (
            f"{name} needs {required}% battery for this task "
            f"but only has {available}%."
        )
        super().__init__(message)


class Robot(abc.ABC):
    """Abstract base class for all robots in the fleet."""

    manufacturer = "Acme Robotics"
    population = 0

    def __init__(self, name: str, battery: int = 100):
        self.name = name
        self._battery = 0
        self.battery = battery  # goes through the clamped setter
        Robot.population += 1

    @property
    def battery(self) -> int:
        return self._battery

    @battery.setter
    def battery(self, value: int) -> None:
        self._battery = max(0, min(100, value))

    def use_battery(self, amount: float) -> None:
        """Shared battery-spending logic used by every subclass's perform_task()."""
        if amount > self.battery:
            raise InsufficientBatteryError(self.name, amount, self.battery)
        self.battery -= amount

    @classmethod
    def from_config(cls, config: dict) -> "Robot":
        """Alternative constructor: build a robot instance from a dict."""
        return cls(**config)

    @abc.abstractmethod
    def perform_task(self, **kwargs):
        """Every subclass must implement its own task behavior."""
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.name} ({self.battery}% battery)"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, battery={self.battery!r})"

def log_action(func):
    """Decorator that logs entry/exit of a robot method, preserving identity."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        logging.info(f"{self.name}: starting {func.__name__}")
        result = func(self, *args, **kwargs)
        logging.info(f"{self.name}: finished {func.__name__}")
        return result

    return wrapper


class CleaningRobot(Robot):
    """A robot that vacuums rooms."""

    def __init__(self, name: str, battery: int = 100, dust_capacity: int = 500):
        super().__init__(name, battery)
        self.dust_capacity = dust_capacity

    @log_action
    def perform_task(self, **kwargs):
        """Vacuum a room, consuming battery."""
        self.use_battery(10)
        return f"{self.name} vacuumed the room (capacity {self.dust_capacity}ml)."