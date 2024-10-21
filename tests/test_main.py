import os
import pytest

from main import load_config, commit_by_tag, get_commits_dependency, create_dot_file

def test_load_config():
    settings = load_config("config.csv")
    assert settings['graphviz_path'] == 'C:/Program Files/Graphviz/bin/dot.exe'
    assert settings['repository_path'] == r'C:\Users\admin\PycharmProjects\vShell'
    assert settings['tag_name'] == 'tag'


def test_commit_by_tag(tmpdir):
    repo_path = tmpdir.mkdir('test_repo')
    git_dir = repo_path.mkdir('.git')
    refs_dir = git_dir.mkdir('refs')
    tags_dir = refs_dir.mkdir('tags')
    tag_file = tags_dir.join('tag')
    tag_file.write('test_commit_hash')
    commit_hash = commit_by_tag(str(repo_path), 'tag')
    assert commit_hash == 'test_commit_hash'


def test_get_commits_dependency(tmpdir):
    with pytest.raises(Exception) as e:
        test_repo = tmpdir.mkdir('test_repo')
        starting_commit_info = 'test_commit_hash'
        get_commits_dependency(str(test_repo), starting_commit_info)
    assert str(e.value) == "Ошибка при чтении или декомпрессии коммита test_commit_hash"


def test_create_dot_file(tmpdir):
    output_file = str(tmpdir.join('output.dot'))
    commits_dict = {
        'commit_id': {'author': 'Test Author', 'message': 'Test Message', 'parent': [], 'date': '2022-02-22', 'files': 'a'}}
    create_dot_file(commits_dict, output_file)
    assert os.path.exists(output_file)