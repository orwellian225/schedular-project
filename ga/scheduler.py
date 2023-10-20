import process
import queues.rr as rrq
import queues.fcfs as fcfsq
import queues.stcf as stcfq

class Scheduler:
    def __init__(self, queues: list[dict[str, int]]):
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
                self.queues.append(fcfsq.FCFS(
                    queue_param['max_drop_t'],
                    queue_param['max_boost_t']
                ))

            if queue_param['type'] == 1: # Shortest To Completion First
                self.queues.append(stcfq.STCF(
                    queue_param['max_drop_t'],
                    queue_param['max_boost_t']
                ))

            if queue_param['type'] == 2: # Round Robin
                self.queues.append(rrq.RR(
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

    def insert(self, new_process):
        new_job = process.Job(new_process)
        self.queues[0].insert(new_job)

    def read(self) -> str:
        for q in self.queues:
            if q.size != 0:
                return q.read()
        
        return ''