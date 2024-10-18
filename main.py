import csv


def load_config(configFile):
    setting = {}
    with open(configFile) as config:
        reader = csv.reader(config, delimiter=',')
        for row in reader:
            setting[row[0]] = row[1]
    return setting

config = load_config('config.csv')
graphviz_path = config['graphviz_path']
repository_path = config['repository_path']
tag_name = config['tag_name']