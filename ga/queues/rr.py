import process

class RRJob:
    def __init__(self, job: process.Job):
        self.job = job
        self.boost_t = 0 # The number of time slices spent waiting (gets reset on read) before boosting
        self.drop_t = 0 # The number of time slices being executed before dropping 
        self.rr_t = 0 # The number of times it gets run sequentially before switching to the next process

    def __lt__(self, other):
        return self.job.process.duration - self.job.executed_steps < other.job.process.duration - other.job.executed_steps


class RR:
    def __init__(self, max_drop_t: int, max_boost_t: int, max_rr: int):
        self.max_drop_t = max_drop_t
        self.max_boost_t = max_boost_t
        self.max_rr = max_rr
        self.drop_q = None
        self.boost_q = None
        self.io_boost_q = None
        self.jobs: list[RRJob] = []
        self.size = 0

    def insert(self, job: process.Job):
        self.jobs.append(RRJob(job))
        self.size += 1

    def read(self) -> str:
        if len(self.jobs) == 0:
            return ''

        self.jobs[0].boost_t = 0
        self.jobs[0].drop_t += 1
        self.jobs[0].rr_t += 1
        output = f'{self.jobs[0].job.read()}'

        if self.jobs[0].job.executed_steps == self.jobs[0].job.process.duration:
            # Remove the job
            self.jobs.pop(0)
            self.size -= 1
            return output # if the job is completely finished, there is no need to check if it needs to be moved

        if self.jobs[0].rr_t == self.max_rr:
            temp = self.jobs[0]
            temp.rr_t = 0
            self.jobs.pop(0)
            self.jobs.append(temp)
            return output

        if self.io_boost_q != None and '!' in output:
            self.io_boost_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1
            return output

        if self.boost_q != None and self.jobs[0].boost_t == self.max_boost_t:
            # Boost the job
            self.boost_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1
            return output

        if self.drop_q != None and self.jobs[0].drop_t == self.max_drop_t:
            # Drop the job
            self.drop_q.insert(self.jobs[0].job)
            self.jobs.pop(0)
            self.size -= 1
            return output

        return output

    def set_boost(self, queue):
        self.boost_q = queue

    def set_drop(self, queue):
        self.drop_q = queue

    def set_io_boost(self, queue):
        self.io_boost_q = queue