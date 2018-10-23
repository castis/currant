import datetime
import json


class Output:

    file = None

    def __init__(self):
        now = datetime.datetime.now().isoformat()
        self.file = open(f'./logs/{now}.txt', 'w')

    def tick(self, engine):
        state = {
            'gyro': engine.vehicle.gyro,
            'accel': engine.vehicle.accel,
        }
        now = datetime.datetime.now().isoformat()
        line = json.dumps(state)
        self.file.write(f'{now}::{line}\n')

    def down(self):
        self.file.close()
