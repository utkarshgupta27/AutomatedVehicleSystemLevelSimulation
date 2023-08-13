import random

class Road:

    def __init__(self):
        # Defining some sample road properties
        self.road_types = ["asphalt", "gravel", "dirt", "snow"]
        self.roughness = {
            "asphalt": 0.1,   # Roughness scale: 0 (smooth) to 1 (very rough)
            "gravel": 0.6,
            "dirt": 0.8,
            "snow": 0.7
        }
        self.friction = {
            "asphalt": 0.9,   # Friction scale: 0 (no friction) to 1 (high friction)
            "gravel": 0.5,
            "dirt": 0.4,
            "snow": 0.3
        }

    def get_road_properties(self, position):
        """
        This function returns road properties based on a given position.
        For simplicity, the road type changes every 100 units of position.
        You can modify the logic to be more sophisticated if needed.
        """

        # Based on position, determine which type of road it is
        road_type = self.road_types[position // 100 % len(self.road_types)]

        return {
            "road_type": road_type,
            "roughness": self.roughness[road_type],
            "friction": self.friction[road_type]
        }


# Example:
# road = Road()
# position = 150  # Sample position
# print(road.get_road_properties(position))
