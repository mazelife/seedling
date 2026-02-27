#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from seedling.motiondetector import Sensor


if __name__ == "__main__":
    # This allows easy placement of apps within the interior
    # seedling directory.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "seedling"))
    logging.basicConfig(level=logging.INFO)
    s = Sensor()
    s.sense(interval_seconds=0.2, window_seconds=5)
