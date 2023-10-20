class Process:
    def __init__(self, name, duration, arrival_time, io_frequency):
        self.name = name
        self.duration = duration
        self.arrival_time = arrival_time
        self.io_frequency = io_frequency

class Job:
    def __init__(self, process: Process):
        self.process = process
        self.executed_steps = 0
        self.io_steps = 0

    def read(self) -> str:
        if self.process.io_frequency != 0 and self.io_steps == self.process.io_frequency and self.executed_steps != self.process.duration:
            self.io_steps = 0
            return f'!{self.process.name}'
        else:
            self.executed_steps += 1
            self.io_steps += 1
            return f'{self.process.name}'