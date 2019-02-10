import glob
import os
import logging
import json
from pylab import plot, subplot, xlabel, ylabel, title, grid, show, legend


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger()


latest = max(glob.iglob("./logs/*.txt"), key=os.path.getmtime)
logger.info(f"Opening {latest}")


time = []
gyro = {"x": [], "y": [], "z": []}
accel = {"x": [], "y": [], "z": []}

with open(latest, "r") as file:
    for line in file:
        pieces = line.split("::")
        time.append(pieces[0])
        data = json.loads(pieces[1])

        gyro["x"].append(data["gyro"]["x"])
        gyro["y"].append(data["gyro"]["y"])
        gyro["z"].append(data["gyro"]["z"])

        accel["x"].append(data["accel"]["x"])
        accel["y"].append(data["accel"]["y"])
        accel["z"].append(data["accel"]["z"])

lines = len(gyro["x"])
logger.info(f"plotting {lines} records")

subplot(2, 1, 1)
title("Gyroscope")
xlabel("time")
ylabel("reading")
plot(
    time,
    gyro["x"],
    color="green",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)
plot(
    time,
    gyro["y"],
    color="red",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)
plot(
    time,
    gyro["z"],
    color="blue",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)

subplot(2, 1, 2)
title("Accelerometer")
xlabel("time")
ylabel("reading")
plot(
    time,
    accel["x"],
    color="green",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)
plot(
    time,
    accel["y"],
    color="red",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)
plot(
    time,
    accel["z"],
    color="blue",
    marker="o",
    linestyle="solid",
    linewidth=1,
    markersize=1,
)

grid(True)

try:
    show()
except KeyboardInterrupt:
    logger.info("Caught ^C, quitting")
