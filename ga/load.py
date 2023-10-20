import process
import re
import os

small_dir = 'Process_List/Small'
medium_dir = 'Process_List/Medium'
large_dir = 'Process_List/Large'
current_dir = large_dir 
def load_data() -> list[list[process.Process]]:

    result = []
    file_regex = re.compile('data_\d+')
    for filepath in os.scandir(current_dir):
        if filepath.is_file() and file_regex.match(filepath.name):
            file = open(filepath)

            processes = []
            num_processes = int(file.readline())

            for _ in range(num_processes):
                process_str = file.readline()
                process_tokens = process_str.split(',')
                processes.append(process.Process(
                    process_tokens[0],
                    int(process_tokens[1]),
                    int(process_tokens[2]),
                    int(process_tokens[3])
                ))

            file.close()

            result.append(processes)

    return result
