import datetime
import json


class Output:
    def __init__(self, state):
        now = datetime.datetime.now().isoformat()
        self.file = open(f"./logs/{now}.txt", "w")

    def tick(self, state):
        line = json.dumps(
            {"time": state.timer.current, "gyro": state.vehicle.gyro, "accel": engine.vehicle.accelerometer}
        )
        self.file.write(f"{line}\n")

    def down(self):
        self.file.close()
