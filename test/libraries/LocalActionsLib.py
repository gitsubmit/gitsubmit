import os
import subprocess

__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""

class LocalActionsLib(object):

    def clone_repo(self, repo_name, working_dir, as_teacher=True):
        if as_teacher:
            git_host = "test_gitsubmit_repo_as_teacher"
        else:
            git_host = "test_gitsubmit_repo_as_student"
        process = subprocess.Popen("git clone " + git_host + ":" + repo_name, shell=True, cwd=working_dir,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not call 'git clone'")

    def clone_known_project(self, working_dir):
        self.clone_repo("test_class/test_project", working_dir=working_dir, as_teacher=True)

    def known_project_should_exist(self, working_dir):
        full_path = os.path.join(working_dir, "test_project")
        if not os.path.exists(full_path):
            raise Exception("Path "+str(full_path)+" does not exist!")

    def write_some_data_to_file(self, full_filepath):
        some_data = "some data\nsome more data"
        if not os.path.exists(os.path.dirname(full_filepath)):
            os.makedirs(os.path.dirname(full_filepath))
        with open(full_filepath, 'w') as w:
            w.write(some_data)

    def generate_complex_file_structure_in_known_repo(self, working_dir):
        full_path = os.path.join(working_dir, "test_project")
        file1 = os.path.join(full_path, "file1.txt")
        self.write_some_data_to_file(file1)
        file2 = os.path.join(full_path, "file2.txt")
        self.write_some_data_to_file(file2)
        filea1 = os.path.join(full_path, "dir_a", "file_a1.txt")
        self.write_some_data_to_file(filea1)
        fileaa1 = os.path.join(full_path, "dir_a", "dir_aa", "file_aa1.txt")
        self.write_some_data_to_file(fileaa1)
        fileaa2 = os.path.join(full_path, "dir_a", "dir_aa", "file_aa2.txt")
        self.write_some_data_to_file(fileaa2)

    def add_files_commit_and_push_in_known_repo(self, working_dir):
        git_working_path = os.path.join(working_dir, "test_project")
        process = subprocess.Popen("git add .", shell=True, cwd=git_working_path,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not call 'git add'")
        process = subprocess.Popen('git commit -m "generate some files to curl from api"', shell=True, cwd=git_working_path,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not call 'git commit'")
        process = subprocess.Popen("git push origin master", shell=True, cwd=git_working_path,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not call git push")

    def get_latest_commit_in_known_repo(self, working_dir):
        git_working_path = os.path.join(working_dir, "test_project")
        process = subprocess.Popen('git log -n 1 --pretty=format:"%H"', shell=True, cwd=git_working_path,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not call git log -n 1 --pretty=format:'%H'")
        return out

    def untracked_files_should_not_exist_in_known_repo(self, working_dir):
        git_working_path = os.path.join(working_dir, "test_project")
        process = subprocess.Popen('git diff --exit-code', shell=True, cwd=git_working_path,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Untracked files exist! See output")

    def do_get_filesystem_from_docker(self, working_dir):
        process = subprocess.Popen('docker cp gitotestname:/home/git/repositories .', shell=True, cwd=working_dir,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print out, err
        if process.returncode != 0:
            raise Exception("Could not copy from docker! see output")

