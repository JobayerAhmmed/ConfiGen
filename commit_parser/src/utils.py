import os
import time
import datetime
import logging
import subprocess
import shutil

import pandas as pd


def create_dir(dir: str):
    """Creates directory and subdirectories if not exist.
    
    Parameters
    ----------
    dir : str
        Pathname of the directory to be created.
    """
    if not os.path.isdir(dir):
        os.makedirs(dir)


def read_csv_to_df(filename: str):
    df = pd.read_csv(filename, header='infer')
    return df


def clone_repo(repo_url: str, project_repo_dir: str, parent_dir: str):
    """Clone a repository and put the code in the specified directory.
    
    Parameters
    ----------
    repo_url : str
        GitHub repository url.
    project_repo_dir : str
        Directory name of the cloned code base.
    parent_dir : str
        Directory where to put the cloned code base.
    """
    logging.info("Cloning {} ...".format(repo_url))
    os.chdir(parent_dir)

    if os.path.exists(project_repo_dir):
        shutil.rmtree(project_repo_dir)
        create_dir(project_repo_dir)
        r = subprocess.run(["git", "clone", repo_url, project_repo_dir])
        if r.returncode != 0:
            logging.error("Failed to clone repo {}".format(repo_url))
            return -1
    else:
        create_dir(project_repo_dir)
        r = subprocess.run(["git", "clone", repo_url, project_repo_dir])
        if r.returncode != 0:
            logging.error("Failed to clone repo {}".format(repo_url))
            return -1
    return 0


def checkout_to_commit(project_config, commit_id):
    if os.path.isdir(project_config.project_repo_dir):
        os.chdir(project_config.project_repo_dir)
    else:
        logging.error('{} repository does not exist. Clone the repo.'
                      .format(project_config.project_name))
        return -1
    r = subprocess.run(['git', 'clean', '-fxdq'])
    if r.returncode != 0:
        logging.error('[{}] Failed to git clean'
                      .format(project_config.project_name))
        return -1
    r = subprocess.run(['git', 'reset', '--hard',
                        'origin/' + commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to git reset to {}'
                      .format(project_config.project_name, commit_id))
        return -1
    r = subprocess.run(['git', 'checkout', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to checkout to {}'
                      .format(project_config.project_name, commit_id))
        return -1
    r = subprocess.run(['git', 'pull', 'origin', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to pull from origin/{}'
                      .format(project_config.project_name, commit_id))
        return -1
    return 0


def reverse_file_data(file):
    df = read_csv_to_df(file)
    reversed_df = df[::-1]
    reversed_df.to_csv(file, header=True, index=False)
