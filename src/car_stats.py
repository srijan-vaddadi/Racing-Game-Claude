"""
Car types and stats definitions.
"""

import random
from typing import Dict, List, Tuple

# Car type definitions with stats
# Types 1-5 represent different vehicle classes, 6 = motorcycle
CAR_TYPES = {
    1: {
        "name": "Sports",
        "max_velocity": 9.0,
        "acceleration": 0.16,
        "handling": 3.5,
        "durability": 0.5,
        "description": "Fast but fragile",
        "is_motorcycle": False
    },
    2: {
        "name": "Muscle",
        "max_velocity": 8.0,
        "acceleration": 0.20,
        "handling": 2.2,
        "durability": 0.8,
        "description": "Great acceleration, poor handling",
        "is_motorcycle": False
    },
    3: {
        "name": "Sedan",
        "max_velocity": 7.0,
        "acceleration": 0.12,
        "handling": 3.0,
        "durability": 1.0,
        "description": "Balanced all-rounder",
        "is_motorcycle": False
    },
    4: {
        "name": "Truck",
        "max_velocity": 5.5,
        "acceleration": 0.06,
        "handling": 1.8,
        "durability": 1.5,
        "description": "Slow but very tough",
        "is_motorcycle": False
    },
    5: {
        "name": "Racer",
        "max_velocity": 10.0,
        "acceleration": 0.22,
        "handling": 4.0,
        "durability": 0.3,
        "description": "Ultimate speed, very fragile",
        "is_motorcycle": False
    },
    6: {
        "name": "Motorcycle",
        "max_velocity": 11.0,
        "acceleration": 0.25,
        "handling": 4.5,
        "durability": 0.2,
        "description": "Fastest, extreme handling, no protection",
        "is_motorcycle": True
    }
}

CAR_COLORS = ["red", "blue", "green", "yellow", "black"]


def get_car_stats(car_type: int) -> Dict:
    """Get stats for a car type."""
    return CAR_TYPES.get(car_type, CAR_TYPES[3])


def get_car_image_name(color: str, car_type: int) -> str:
    """Get the image filename for a car/motorcycle."""
    stats = CAR_TYPES.get(car_type, CAR_TYPES[3])
    if stats.get("is_motorcycle"):
        return f"motorcycles/motorcycle_{color}.png"
    return f"cars/car_{color}_{car_type}.png"


def get_random_car() -> Tuple[str, int]:
    """Get a random color and type combination."""
    color = random.choice(CAR_COLORS)
    car_type = random.randint(1, 6)  # Include motorcycle
    return color, car_type


def get_all_car_types() -> List[Dict]:
    """Get list of all car types with their info."""
    return [{"type": k, **v} for k, v in CAR_TYPES.items()]
