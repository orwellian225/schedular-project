import process

class FCFSJob:
    def __init__(self, job: process.Job):
        self.job = job
        self.boost_t = 0 # The number of time slices spent waiting (gets reset on read) before boosting
        self.drop_t = 0 # The number of time slices being executed before dropping 

class FCFS:
    def __init__(self, max_drop_t: int, max_boost_t: int):
        self.max_drop_t = max_drop_t
        self.max_boost_t = max_boost_t
        self.drop_q = None
        self.boost_q = None
        self.jobs: list[FCFSJob] = []
        self.size = 0

    def insert(self, job: process.Job):
        self.jobs.append(FCFSJob(job))
        self.size += 1

    def read(self) -> str:
        if len(self.jobs) == 0:
            return ''

        self.jobs[0].boost_t = 0
        self.jobs[0].drop_t += 1
        output = f'{self.jobs[0].job.read()}'

        if self.jobs[0].job.executed_steps == self.jobs[0].job.process.duration:
            # Remove the job
            self.jobs.pop(0)
            self.size -= 1

        if '!' in output:
            self.io_boost_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1

        if self.boost_q != None and self.jobs[0].boost_t == self.max_boost_t:
            # Boost the job
            self.boost_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1

        if self.drop_q != None and self.jobs[0].drop_t == self.max_drop_t:
            # Drop the job
            self.drop_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1

        return output

    def set_boost(self, queue):
        self.boost_q = queue

    def set_drop(self, queue):
        self.drop_q = queue

    def set_io_boost(self, queue):
        self.io_boost_q = queue