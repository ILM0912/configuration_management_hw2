import csv
import subprocess
from datetime import datetime, timedelta, timezone
import os
import zlib

def load_config(config_file):
    setting = {}
    with open(config_file, encoding='UTF-8') as config:
        reader = csv.reader(config)
        for row in reader:
            if len(row)>1:
                setting[row[0]] = row[1]
    return setting

def commit_by_tag(repo_path, tag_name):
    tag_file_path = os.path.join(repo_path, ".git", "refs", "tags", tag_name)
    if len(tag_name)>0 and os.path.exists(tag_file_path):
        with open(tag_file_path, "r") as tag_file:
            tag_commit_hash = tag_file.read().strip()
    else:
        print(f"\033[33mНет коммита с тегом {tag_name}, граф построен для последнего коммита\033[0m")
        with open(os.path.join(repo_path, ".git", "HEAD"), "r") as head_file:
            head_content = head_file.read().strip()
            if head_content.startswith("ref:"):
                branch_file_path = os.path.join(repo_path, ".git", head_content[5:])
                with open(branch_file_path, "r") as branch_file:
                    tag_commit_hash = branch_file.read().strip()
            else:
                print("Ошибка при получении последнего коммита")
                exit(1)
    return tag_commit_hash


def get_commits_dependency(repo_path, starting_commit_info):
    commits = {}
    commit_hashes = [starting_commit_info]
    while commit_hashes:
        current_commit_hash = commit_hashes.pop(0)
        commit_path = os.path.join(repo_path, ".git", "objects", current_commit_hash[:2], current_commit_hash[2:])
        try:
            with open(commit_path, "rb") as commit_file:
                decompressed_content = zlib.decompress(commit_file.read())
                decoded_content = decompressed_content.decode('utf-8').splitlines()
                parent_hashes = []
                for line in decoded_content:
                    if line.startswith('author'):
                        author = line.split(' ')[1]
                        timestamp = line.split(' ')[3]
                        timezone_offset = line.split(' ')[4]
                        datetime_utc = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
                        hours = int(timezone_offset[:3])
                        minutes = int(timezone_offset[3:])
                        timezone_offset = timedelta(hours=hours, minutes=minutes)
                        datetime_timezone = datetime_utc + timezone_offset
                        date = datetime_timezone.strftime('%d.%m.%Y %H:%M')
                    if line.startswith('parent'):
                        parent_hashes+=[line.split(' ')[1]]
                message = decoded_content[-1]
                subprocess.run(['git', 'config', '--global', 'core.pager', "'less --raw-control-chars'"], cwd=repo_path)
                result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', current_commit_hash], cwd=repo_path, capture_output=True, text=True, check=True, encoding='UTF-8')
                result = result.stdout.splitlines()
                files_string = ""
                for file in result:
                    type, file_name = file.split('\t')
                    files_string += f"{file_name} --- {type}\n"
                commit_info = {
                    'author': author,
                    'message': message,
                    'parent': parent_hashes,
                    'date': date,
                    'files': files_string
                }
                commits[current_commit_hash] = commit_info
                commit_hashes.extend(parent_hashes)
        except Exception as e:
            error_message = f"Ошибка при чтении или декомпрессии коммита {current_commit_hash}"
            raise Exception(error_message)
    return commits


def create_dot_file(commits_dict, output_file):
    with open(output_file, 'w', encoding='UTF-8') as file:
        file.write('digraph CommitGraph {\nnode [shape=rect, color=blue]')
        for commit_id, commit_info in commits_dict.items():
            author = commit_info['author']
            message = commit_info['message']
            date = commit_info['date']
            files = commit_info['files']
            if len(files)>0:
                file.write(f'\n\n"{commit_id}" [label="hexsha: {commit_id}\nauthor: {author}\nmessage: {message}\ndate: {date}\n\nchanged files\n{files}"];\n')
            else:
                file.write(f'\n\n"{commit_id}" [label="hexsha: {commit_id}\nauthor: {author}\nmessage: {message}\ndate: {date}"];\n')
            for parent_id in commit_info['parent']:
                file.write(f'"{parent_id}" -> "{commit_id}";\n')
        file.write('}\n')

def main():
    config = load_config('config.csv')
    graphviz_path = config['graphviz_path']
    repository_path = config['repository_path']
    tag_name = config['tag_name']
    commits_dict = get_commits_dependency(repository_path, commit_by_tag(repository_path, tag_name))
    create_dot_file(commits_dict, 'commit_graph.dot')
    subprocess.run([graphviz_path, '-Tpng', 'commit_graph.dot', '-o', 'commit_graph.png'])
    print('\033[92mГраф зависимостей успешно построен, находится в файле проекта - commit_graph.png\033[0m')

if __name__ == "__main__":
    main()