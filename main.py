import csv
from pprint import pprint

import git

def load_config(config_file):
    setting = {}
    with open(config_file, encoding='UTF-8') as config:
        reader = csv.reader(config)
        for row in reader:
            if len(row)>1:
                setting[row[0]] = row[1]
    return setting

def commit_by_tag(repo, tag_name):
    for tag in repo.tags:
        if tag.name == tag_name:
            return tag.commit
    print(f"Нет коммита с тегом {tag_name}, граф построен для последнего коммита")
    return repo.head.commit

def get_commits_dependency(repo, commit):
    commit_history = list(commit.iter_items(repo, rev=commit))
    commits_dict = {}
    for commit in commit_history:
        files_changed = [item for item in commit.stats.files]
        commit_info = {
            'author': commit.author.name,
            'message': commit.message,
            'files': files_changed,
            'parent': [i.hexsha for i in commit.parents]
        }
        commits_dict[commit.hexsha] = commit_info
    return commits_dict


config = load_config('config.csv')
graphviz_path = config['graphviz_path']
repository_path = config['repository_path']
tag_name = config['tag_name']
repo = git.Repo(repository_path)
pprint(get_commits_dependency(repo,commit_by_tag(repo, tag_name)))
