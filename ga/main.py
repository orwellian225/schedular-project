import load
import math as m
import scheduler
import evaluate


def main():
    all_processes = load.load_data()
    
    scheduler_structure = [
        { "type": 0, "drop_q": 1, "boost_q": -1, "max_drop_t": 1, "max_boost_t": -1, "io_boost_q": -1 },
        { "type": 1, "drop_q": -1, "boost_q": -1, "max_drop_t": -1, "max_boost_t": -1, "io_boost_q": -1 }
    ]

    turnaround_avg = 0
    response_avg = 0
    burst_avg = 0
    switch_avg = 0
    score_avg = 0

    for i, processes in enumerate(all_processes):
        output = ""
        max_time = 0
        for p in processes:
            max_time += p.duration
            max_time += m.floor((p.duration - 1) / p.io_frequency ) if p.io_frequency != 0 else 0

        test_scheduler = scheduler.Scheduler(scheduler_structure)
        next_process_idx = 0
        for t in range(0, max_time):
            while next_process_idx < len(processes) and t == processes[next_process_idx].arrival_time:
                next_process = processes[next_process_idx]
                test_scheduler.insert(next_process)
                next_process_idx += 1

            output += f'{test_scheduler.read()} '

        (turnaround, response, burst, switch, score) = evaluate.evaluate_schedule(output, processes)

        turnaround_avg += turnaround
        response_avg += response
        burst_avg += burst
        switch_avg += switch
        score_avg += score
        print(f'{i}: {turnaround:.2f}, {response:.2f}, {burst:.2f}, {switch:.2f}, {score:.2f}')
    
    num_runs = len(all_processes)
    turnaround_avg /= num_runs
    response_avg /= num_runs
    burst_avg /= num_runs
    switch_avg /= num_runs
    score_avg /= num_runs
    print(f'average: {turnaround_avg:.2f}, {response_avg:.2f}, {burst_avg:.2f}, {switch_avg:.2f}, {score_avg:.2f}')

if __name__ == '__main__':
    main()