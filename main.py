import csv
import subprocess
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


def create_dot_file(commits_dict, output_file):
    with open(output_file, 'w', encoding='UTF-8') as file:
        file.write('digraph CommitGraph {\n')
        for commit_id, commit_info in commits_dict.items():
            author = commit_info['author']
            message = commit_info['message']
            files_string = '\n'.join([f"{file}" for file in commit_info['files']])
            file.write(f'\n\n"{commit_id}" [label="author: {author}\nmessage: {message}\nfiles: {files_string}"];\n')
            for parent_id in commit_info['parent']:
                file.write(f'"{parent_id}" -> "{commit_id}";\n')
        file.write('}\n')

config = load_config('config.csv')
graphviz_path = config['graphviz_path']
repository_path = config['repository_path']
tag_name = config['tag_name']
repo = git.Repo(repository_path)
create_dot_file(get_commits_dependency(repo,commit_by_tag(repo, tag_name)), 'commit_graph.dot')
subprocess.run([graphviz_path, '-Tpng', 'commit_graph.dot', '-o', 'commit_graph.png'])
