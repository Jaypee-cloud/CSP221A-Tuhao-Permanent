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

class DroneRobot(Robot):
    """A robot that flies survey missions."""

    def __init__(self, name: str, battery: int = 100, max_altitude: int = 120):
        super().__init__(name, battery)
        self.max_altitude = max_altitude

    @log_action
    def perform_task(self, **kwargs):
        """Fly a survey pass, consuming battery."""
        self.use_battery(25)
        return f"{self.name} flew a survey pass up to {self.max_altitude}m."

class CarRobot(Robot):
    """A ground transport robot that navigates land routes."""

    def __init__(self, name: str, battery: int = 100, top_speed: int = 60):
        super().__init__(name, battery)
        self.top_speed = top_speed

    @log_action
    def perform_task(self, **kwargs):
        """Drive a delivery route, consuming battery."""
        self.use_battery(15)
        return f"{self.name} drove a delivery route at speeds up to {self.top_speed} km/h."


def fleet_report(robots: list[Robot]) -> None:
    """Print a status line for every robot without branching on subclass."""
    for robot in robots:
        print(str(robot))


def run_task_safely(robot: Robot, **kwargs):
    """Run a robot's task, handling InsufficientBatteryError gracefully."""
    try:
        result = robot.perform_task(**kwargs)
    except InsufficientBatteryError as exc:
        logging.error(str(exc))
    else:
        print(result)
    finally:
        print(f"{robot.name} battery is now {robot.battery}%.")

# ---------------------------------------------------------------------------
# 1.8 The Mutable Class Attribute Trap - standalone demonstration.
# This is NOT part of the Robot hierarchy above; it's purely to show the bug.
# ---------------------------------------------------------------------------

class BuggyLogger:
    """BUGGY: a list defined at class level is shared by every instance."""

    entries = []  # <- lives on the class, not the instance

    def log(self, message: str) -> None:
        self.entries.append(message)


class FixedLogger:
    """FIXED: the list is created fresh in __init__, so it's per-instance."""

    def __init__(self):
        self.entries = []

    def log(self, message: str) -> None:
        self.entries.append(message)


def demonstrate_mutable_class_attribute_trap() -> None:
    print("--- Buggy version (shared list) ---")
    buggy_a = BuggyLogger()
    buggy_b = BuggyLogger()
    buggy_a.log("a's message")
    buggy_b.log("b's message")
    print("buggy_a.entries:", buggy_a.entries)
    print("buggy_b.entries:", buggy_b.entries)
    print("Same object?", buggy_a.entries is buggy_b.entries)

    print("\n--- Fixed version (per-instance list) ---")
    fixed_a = FixedLogger()
    fixed_b = FixedLogger()
    fixed_a.log("a's message")
    fixed_b.log("b's message")
    print("fixed_a.entries:", fixed_a.entries)
    print("fixed_b.entries:", fixed_b.entries)
    print("Same object?", fixed_a.entries is fixed_b.entries)

    
def main() -> None:
    roomba = CleaningRobot("Roomba", battery=100, dust_capacity=500)
    drone = DroneRobot("Aqua-Drone", battery=15, max_altitude=200)
    car = CarRobot("Speedy", battery=100, top_speed=80)

    print(f"repr(roomba) -> {roomba!r}")
    print(f"Robot.population -> {Robot.population}\n")

    fleet_report([roomba, drone, car])
    print()

    run_task_safely(roomba)
    run_task_safely(drone)
    run_task_safely(drone)  # second flight should fail: not enough battery
    run_task_safely(car)
    print()

    demonstrate_mutable_class_attribute_trap()


if __name__ == "__main__":
    main()