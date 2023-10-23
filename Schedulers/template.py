import sys
import json
import math as m

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Define the process data clas
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

class FCFSJob:
    def __init__(self, job: Job):
        self.job = job
        self.boost_t = 0 # The number of time slices spent waiting (gets reset on read) before boosting
        self.drop_t = 0 # The number of time slices being executed before dropping 

class FCFS:
    def __init__(self, max_drop_t: int, max_boost_t: int):
        self.max_drop_t = max_drop_t
        self.max_boost_t = max_boost_t
        self.drop_q = None
        self.boost_q = None
        self.io_boost_q = None
        self.jobs: list[FCFSJob] = []
        self.size = 0

    def insert(self, job: Job):
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

class STCFJob:
    def __init__(self, job: Job):
        self.job = job
        self.boost_t = 0 # The number of time slices spent waiting (gets reset on read) before boosting
        self.drop_t = 0 # The number of time slices being executed before dropping 

    def __lt__(self, other):
        return self.job.process.duration - self.job.executed_steps < other.job.process.duration - other.job.executed_steps


class STCF:
    def __init__(self, max_drop_t: int, max_boost_t: int):
        self.max_drop_t = max_drop_t
        self.max_boost_t = max_boost_t
        self.drop_q = None
        self.boost_q = None
        self.io_boost_q = None
        self.jobs: list[STCFJob] = []
        self.size = 0

    def insert(self, job: Job):
        self.jobs.append(STCFJob(job))
        self.size += 1

        self.jobs.sort()

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
            return output # if the job is completely finished, there is no need to check if it needs to be moved

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

class RRJob:
    def __init__(self, job: Job):
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

    def insert(self, job: Job):
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

def construct_scheduler_structure(genome: int) -> list[dict[str, int]]:
    num_queue_types = 3
    num_queues = ( genome >> 768 ) + 1

    structure = []

    queue_genome_length = 48
    for i in range(num_queues):
        queue_genome = ( genome >> (768 - (i + 1) * queue_genome_length) ) & (2**queue_genome_length - 1)

        queue_type = ( queue_genome >> (queue_genome_length - 2 ) ) % num_queue_types
        queue_drop = (( queue_genome >> queue_genome_length - 6 ) & 0xf ) % num_queues 
        queue_boost = (( queue_genome >> queue_genome_length - 12 ) & 0xf ) % num_queues
        queue_io_boost = (( queue_genome >> queue_genome_length - 16 ) & 0xf ) % num_queues
        queue_drop_t = ( queue_genome >> queue_genome_length - 24 ) & 0xff
        queue_boost_t = ( queue_genome >> queue_genome_length - 32 ) & 0xff
        queue_rr_t = ( queue_genome >> queue_genome_length - 40 ) & 0xff

        structure.append({
            "type": queue_type, 
            "drop_q": queue_drop if queue_drop != i else -1,
            "boost_q": queue_boost if queue_boost != i else -1,
            "io_boost_q": queue_io_boost if queue_io_boost != i else -1,
            "max_drop_t": queue_drop_t,
            "max_boost_t": queue_boost_t,
            "max_rr_t": queue_rr_t
        })

    return structure

class Scheduler:
    def __init__(self, queues: list[dict[str, int]], ):
        self.queues  = []

        """
        All Queue Parameters
            * type - Which type of queue is used
                * 0 -> FCFS
                * 1 -> STCF
                * 2 -> RR
            * max_drop_t - Max amount of time that a job can be executed for in this queue
                * -1 -> no time limit
            * drop_q - The index of the queue to drop a job to
                * -1 -> don't drop the job
            * max_boost_t - Max amount of time that a job can can wait for in this queue 
                * -1 -> no time limit
            * boost_q - The index of the next queue to boost a job to
                * -1 -> don't boost the job
            * io_boost_q - The index of the queue to boost a job to when it has an IO request
            * max_rr_t - The max number of sequential times running a process in round robin, before moving to the next process
        """

        for i in range(0, len(queues)):
            queue_param = queues[i]

            if queue_param['type'] == 0: # First Come First Serve 
                self.queues.append(FCFS(
                    queue_param['max_drop_t'],
                    queue_param['max_boost_t']
                ))

            if queue_param['type'] == 1: # Shortest To Completion First
                self.queues.append(STCF(
                    queue_param['max_drop_t'],
                    queue_param['max_boost_t']
                ))

            if queue_param['type'] == 2: # Round Robin
                self.queues.append(RR(
                    queue_param['max_drop_t'],
                    queue_param['max_boost_t'],
                    queue_param['max_rr_t']
                ))

        for i in range(0, len(queues)):
            queue_param = queues[i]
            if queue_param['boost_q'] != -1:
                self.queues[i].set_boost(self.queues[queue_param['boost_q']])
            if queue_param['drop_q'] != -1:
                self.queues[i].set_drop(self.queues[queue_param['drop_q']])
            if queue_param['io_boost_q'] != -1:
                self.queues[i].set_io_boost(self.queues[queue_param['io_boost_q']])

    def insert(self, process):
        new_job = Job(process)
        self.queues[0].insert(new_job)

    def read(self) -> str:
        for q in self.queues:
            if q.size != 0:
                return q.read()
        
        return ''


def main():
    # Check if the correct number of arguments is provided
    import sys
    if len(sys.argv) != 2:
        return 1

    # Extract the input file name from the command line arguments
    input_file_name = f"Process_List/{config['dataset']}/{sys.argv[1]}"

    # Define the number of processes
    num_processes = 0

    # Initialize an empty list for process data
    data_set: list[Process] = []

    # Open the file for reading
    try:
        with open(input_file_name, "r") as file:
            # Read the number of processes from the file
            num_processes = int(file.readline().strip())

            # Read process data from the file and populate the data_set list
            for _ in range(num_processes):
                line = file.readline().strip()
                name, duration, arrival_time, io_frequency = line.split(',')
                process = Process(name, int(duration), int(arrival_time), int(io_frequency))
                data_set.append(process)

    except FileNotFoundError:
        print("Error opening the file.")
        return 1

    output = ""
    max_time = 0
    for p in data_set:
        max_time += p.duration
        max_time += m.floor((p.duration - 1) / p.io_frequency ) if p.io_frequency != 0 else 0

    genome = 6794754254355170913406781093340568290949153219954559846922636346711752677269652499655125485674167421237562887824717810636356715124886980125788104449007509254337865411297272303893811997611822005705118127544471045402318763003930730348
    structure = construct_scheduler_structure(genome)
    scheduler = Scheduler(structure)
    next_process_idx = 0
    for t in range(0, max_time):
        while next_process_idx < len(data_set) and t == data_set[next_process_idx].arrival_time:
            next_process = data_set[next_process_idx]
            scheduler.insert(next_process)
            next_process_idx += 1

        output += f'{scheduler.read()} '


    # output = "AB AC AB !AD BA CB !BL BX AB" #Example output


    # Open a file for writing
    try:
        output_path = f"Schedulers/template/{config['dataset']}/template_out_{sys.argv[1].split('_')[1]}"
        with open(output_path, "w") as output_file:
            # Write the final result to the output file
            output_file.write(output)

    except IOError:
        print("Error opening the output file.")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
