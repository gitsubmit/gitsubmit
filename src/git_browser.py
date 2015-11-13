import os
import subprocess
from config import STATIC_REPOS_ROOT
from git import Repo
from git import Git

__author__ = 'shawkins'


class RepoDoesNotExistError(Exception): pass


class GitRepo(object):

    def __init__(self, full_uri):

        STATIC_REPOS_ROOT = ""

        repo_exists = os.path.exists(STATIC_REPOS_ROOT + full_uri)
        self.repo_path = os.path.abspath(STATIC_REPOS_ROOT + full_uri)
        if not repo_exists:
            raise RepoDoesNotExistError(str(STATIC_REPOS_ROOT + full_uri) + " could not be found on this server!")
        self.repo = Repo(self.repo_path)
        self.git = Git(self.repo_path)

    def get_file_or_directory(self, commit_or_branch, path):
        if commit_or_branch in self.repo.branches:
            commit = self.repo.branches[commit_or_branch].commit
        else:
            commit = self.repo.commit(commit_or_branch)
        tree = commit.tree
        file = tree[path]

        object = {
            'type': file.type
        }

        if file.type == "tree":
            object['file_list'] = []
            for i in file:
                print i.name
                object['file_list'].append({'type': i.type, 'name': i.name})
        elif file.type == "blob":
            object['content'] = file.data_stream.read()

        return object


# g = GitRepo("/Users/shawkins/Code/gitsubmit")
# print g.get_file_or_directory("f94e9fb83424", "test/0_web_interface")
# print g.get_file_or_directory("f94e9fb83424", "test/0_web_interface/login.robot")