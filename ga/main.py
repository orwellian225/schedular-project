import load
import math as m
import scheduler
import evaluate
import genome
import time
import csv

def main():
    all_processes = load.load_data()
    initial_pop_size = 5000
    final_pop_size = 100
    decrease_pop_frequency = 100
    population = []

    for _ in range(initial_pop_size):
        population.append({
            "genome": genome.random_genome(),
            "turnaround": 0,
            "response": 0,
            "burst": 0,
            "switch": 0,
            "score": 0,
        })

    headers = ['genome', 'turnaround', 'response', 'burst', 'switch', 'score']
    output_csv = open('ga_best.csv', 'w', newline='')
    csv_writer = csv.DictWriter(output_csv, fieldnames=headers)
    csv_writer.writeheader()

    start_t = time.time()
    current_popsize = initial_pop_size
    current_gen = 0
    print('Generation', current_gen)
    while (True):
        for j in range(current_popsize):
            scheduler_structure = genome.construct_scheduler_structure(population[j]["genome"])

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
                # print(f'{i}: {turnaround:.2f}, {response:.2f}, {burst:.2f}, {switch:.2f}, {score:.2f}')
            
            num_runs = len(all_processes)
            turnaround_avg /= num_runs
            response_avg /= num_runs
            burst_avg /= num_runs
            switch_avg /= num_runs
            score_avg /= num_runs
            population[j]["turnaround"] = turnaround_avg
            population[j]["response"] = response_avg
            population[j]["burst"] = burst_avg
            population[j]["switch"] = switch_avg
            population[j]["score"] = score_avg
            # print(f'{j} average: {turnaround_avg:.2f}, {response_avg:.2f}, {burst_avg:.2f}, {switch_avg:.2f}, {score_avg:.2f}')

        end_t = time.time()
        duration = end_t - start_t

        # print(f'pop size {current_popsize} took {duration} seconds')

        population.sort(key = lambda pop: pop["score"])

        new_population = []

        top_quartile_size = m.floor(current_popsize * 0.25);
        # If uneven amount of top 25%, just remove the worst performer of the 25% to get even
        top_quartile_size = top_quartile_size -1 if top_quartile_size % 2 != 0 else top_quartile_size
        top_quartile = population[:top_quartile_size + 1]

        if current_popsize > final_pop_size and current_gen % decrease_pop_frequency == 0:
            current_popsize -= initial_pop_size // final_pop_size

        children_per_pair = m.floor((current_popsize - top_quartile_size) / (top_quartile_size / 2))
        for i in range(0, top_quartile_size, 2):
            new_population.append(top_quartile[i])
            new_population.append(top_quartile[i + 1])

            for ii in range(children_per_pair):
                # Picking segment length of 4 because most params are of size 4 or 8, so all or half of a value is copied
                child_genome = genome.genome_crossover(top_quartile[i]["genome"], top_quartile[i + 1]["genome"], 4) 

                if ii > 0:
                    child_genome = genome.genome_mutation(child_genome, 772, ii * 4)

                new_population.append({
                    "genome": child_genome,
                    "turnaround": 0,
                    "response": 0,
                    "burst": 0,
                    "switch": 0,
                    "score": 0,
                })

        # if any pop spaces are left over, just introduce a random new genome
        new_pop_difference = current_popsize - len(new_population)
        for _ in range(new_pop_difference):
            new_population.append({
                "genome": genome.random_genome(),
                "turnaround": 0,
                "response": 0,
                "burst": 0,
                "switch": 0,
                "score": 0,
            })

        csv_writer.writerows(population[:1])
        current_gen += 1
        print('Generation', current_gen)
        population = new_population


if __name__ == '__main__':
    main()