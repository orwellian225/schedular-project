import numpy as np

def evaluate_schedule(schedule, processes) -> list[float]:
    metrics = []
    split_schedule = np.array(schedule.split(' '))

    for process in processes:
        name = process.name
        occurances = np.where(split_schedule == name)[0]

        arrival_time = process.arrival_time
        first_run_time = occurances[0]
        complete_time = occurances[-1]

        turnaround = complete_time - arrival_time
        response = first_run_time - arrival_time
        burst = occurances[-1] - occurances[0]

        metrics.append([turnaround, response, burst])

    switch = 0
    for i in range(len(split_schedule) - 1):
        if split_schedule[i] != split_schedule[i + 1]:
            switch += 1

    metrics = np.array(metrics)
    avg_metrics = np.mean(metrics, axis = 0).round(2)

    score = 0.2 * avg_metrics[0] + \
            0.6 * avg_metrics[1] + \
            0.1 * avg_metrics[2] + \
            0.1 * switch 

    # turnaround, response, burst, switch, score
    return (avg_metrics[0], avg_metrics[1], avg_metrics[2], switch, score)

        