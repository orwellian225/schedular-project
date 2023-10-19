import json

param_filepath = './scheduler_params.json'
def main():

    param_file = open(param_filepath)

    data = json.load(param_file)

    mlqf = {
        "small": data["mlqf"]["results"][0]["score"],
        "medium": data["mlqf"]["results"][1]["score"],
        "large": data["mlqf"]["results"][2]["score"],
    }

    results = {}
    for config in data['my_configs']:
        results[config['name']] = { 
            "small": config["results"][0]["score"], 
            "medium": config["results"][1]["score"], 
            "large": config["results"][2]["score"]
        }

    for key in results.keys():
        print(f'Score percentage of mlqf for {key}')
        for size in results[key].keys():
            percentage_of_mlqf = results[key][size] / mlqf[size] * 100
            print(f'\t{size}: {percentage_of_mlqf: .2f}%')

    

if __name__ == '__main__':
    main()