""" Collect commit ids and commit data from a subject's GitHub repository."""

import subprocess
import os
import logging

import pandas as pd
from git import Repo
import progressbar

from utils import *



def run_commit_data(project_config):
    get_commit_ids(project_config)
    get_commit_data(project_config)
    pass


def get_commit_ids(project_config):
    """Get commit ids from a subject's repository.
    Extract fields sha and commit.committer.date, and write them in a csv file.
    """
    logging.info('[{}] Getting commit ids...'
                 .format(project_config.project_name))
    if os.path.isdir(project_config.project_repo_dir):
        os.chdir(project_config.project_repo_dir)
    else:
        logging.error('{} repository does not exist. Clone the repo.'
                      .format(project_config.project_name))
        return

    # If repo is in a different branch or commit, it will extract
    # commits till to that branch or commit.
    # So, checkout to repo_branch from origin before extracting commit ids.
    r = subprocess.run(['git', 'clean', '-fxdq'])
    if r.returncode != 0:
        logging.error('[{}] Failed to git clean'
                      .format(project_config.project_name))
        return
    r = subprocess.run(['git', 'reset', '--hard',
                        'origin/' + project_config.repo_branch])
    if r.returncode != 0:
        logging.error('[{}] Failed to git reset to {}'
                      .format(project_config.project_name,
                              project_config.repo_branch))
        return
    r = subprocess.run(['git', 'checkout', project_config.repo_branch])
    if r.returncode != 0:
        logging.error('[{}] Failed to checkout to {}'
                      .format(project_config.project_name,
                              project_config.repo_branch))
        return
    r = subprocess.run(['git', 'pull', 'origin', project_config.repo_branch])
    if r.returncode != 0:
        logging.error('[{}] Failed to pull from origin/{}'
                      .format(project_config.project_name,
                              project_config.repo_branch))
        return
    
    result = []
    repo = Repo(project_config.project_repo_dir)
    for commit in repo.iter_commits(project_config.repo_branch):
        if len(commit.parents) > 1:
            continue
        result.append({'sha': commit.hexsha, 
                       'commit.committer.date': commit.committed_datetime})
    result.reverse()

    # Discard commit ids before start_commit_id and after end_commit_id
    start_commit_index = next((i for i, obj in enumerate(
        result) if obj['sha'] == project_config.start_commit_id), None)
    end_commit_index = next((i for i, obj in enumerate(
        result) if obj['sha'] == project_config.end_commit_id), None)
    if start_commit_index is None:
        start_commit_index = 0
        logging.warn('[{}] Cannot find start commit index.'
                      .format(project_config.project_name))
    if end_commit_index is None:
        end_commit_index = len(result) - 1
        logging.warn('[{}] Cannot find end commit index.'
                      .format(project_config.project_name))

    if len(result) > 0:
        result = result[start_commit_index:end_commit_index + 1]
        df = pd.DataFrame(result)
        df['commit.committer.date'] = pd.to_datetime(
            df['commit.committer.date'], utc=True)
        # Do not sort by date, will mess the commit-parent order.
        df.to_csv(project_config.file_commit_ids, header=True, index=False)


def get_commit_data(project_config):
    """Get commit data for all commits from a subject's repository.
    Extract data fields and write them in a csv file.
    """
    logging.info('[{}] Getting commit data...'
                 .format(project_config.project_name))
    commit_ids = read_csv_to_df(project_config.file_commit_ids)
    repo = Repo(project_config.project_repo_dir)

    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    change_type = {'A': 'added', 'C': 'copied', 'D': 'removed', 'R': 'renamed', 
                   'M': 'modified', 'T': 'changed', 'U': 'unchanged'}
    bar = progressbar.ProgressBar(max_value=commit_ids.shape[0],
                                  redirect_stdout=True).start()
    data = []
    for index, row in commit_ids.iterrows():
        commit = repo.commit(row['sha'])
        parent = commit.parents[0] if commit.parents else None
        
        obj = {}
        obj['sha'] = commit.hexsha
        obj['commit.committer.date'] = commit.committed_datetime
        obj['commit.comment_count'] = 0
        obj['stats.total'] = commit.stats.total['lines']
        obj['stats.additions'] = commit.stats.total['insertions']
        obj['stats.deletions'] = commit.stats.total['deletions']
        obj['parents'] = [{'sha': item.hexsha} for item in commit.parents]
        obj['files'] = []
        if parent:
            diffs = parent.diff(commit, create_patch=True)
            for diff in diffs:
                file_obj = {}
                if diff.new_file: # new file
                    file_obj['sha'] = diff.b_blob.hexsha
                    file_obj['filename'] = diff.b_path
                    file_obj['status'] = change_type['A']
                    file_obj['additions'] = commit.stats.files[diff.b_path]['insertions']
                    file_obj['deletions'] = commit.stats.files[diff.b_path]['deletions']
                    file_obj['changes'] = commit.stats.files[diff.b_path]['lines']
                elif diff.deleted_file: # deleted file
                    file_obj['sha'] = diff.a_blob.hexsha
                    file_obj['filename'] = diff.a_path
                    file_obj['status'] = change_type['D']
                    file_obj['additions'] = commit.stats.files[diff.a_path]['insertions']
                    file_obj['deletions'] = commit.stats.files[diff.a_path]['deletions']
                    file_obj['changes'] = commit.stats.files[diff.a_path]['lines']
                elif diff.renamed_file:
                    file_obj['sha'] = ''
                    file_obj['filename'] = diff.b_path
                    file_obj['status'] = change_type['R']
                    file_obj['additions'] = commit.stats.files[diff.b_path]['insertions']
                    file_obj['deletions'] = commit.stats.files[diff.b_path]['deletions']
                    file_obj['changes'] = commit.stats.files[diff.b_path]['lines']
                elif diff.copied_file:
                    file_obj['sha'] = diff.b_blob.hexsha
                    file_obj['filename'] = diff.b_path
                    file_obj['status'] = change_type['C']
                    file_obj['additions'] = commit.stats.files[diff.b_path]['insertions']
                    file_obj['deletions'] = commit.stats.files[diff.b_path]['deletions']
                    file_obj['changes'] = commit.stats.files[diff.b_path]['lines']
                else:
                    if diff.b_blob:
                        file_obj['sha'] = diff.b_blob.hexsha
                    file_obj['filename'] = diff.b_path
                    file_obj['status'] = change_type['M']
                    if diff.change_type:
                        file_obj['status'] = change_type[diff.change_type]
                    file_obj['additions'] = commit.stats.files[diff.b_path]['insertions']
                    file_obj['deletions'] = commit.stats.files[diff.b_path]['deletions']
                    file_obj['changes'] = commit.stats.files[diff.b_path]['lines']
                file_obj['patch'] = diff.diff
                obj['files'].append(file_obj)
        else: # first commit
            diffs = commit.diff(EMPTY_TREE_SHA, create_patch=True)
            for diff in diffs:
                file_obj = {}
                file_obj['sha'] = diff.a_blob.hexsha
                file_obj['filename'] = diff.a_path
                file_obj['status'] = change_type['A']
                file_obj['additions'] = commit.stats.files[diff.a_path]['insertions']
                file_obj['deletions'] = commit.stats.files[diff.a_path]['deletions']
                file_obj['changes'] = commit.stats.files[diff.a_path]['lines']
                # Every line is started with -, replace them with +
                # Also, reverse the line numbers for the patch
                lines = diff.diff.split(b'\n')
                if len(lines) > 0:
                    lines[0] = bytes('@@ -0,0 +1,' + str(file_obj['additions'])
                                     + ' @@', encoding='utf-8')
                    for k in range(1, len(lines)):
                        if len(lines[k]) > 1:
                            lines[k] = b'+' + lines[k][1:]
                        else:
                            lines[k] = b'+'
                file_obj['patch'] = b'\n'.join(lines)
                obj['files'].append(file_obj)
        data.append(obj)
        bar.update(index)
    bar.finish()

    data = pd.DataFrame(data)
    data['commit.committer.date'] = pd.to_datetime(
        data['commit.committer.date'], utc=True)
    data.to_csv(project_config.file_commit_data, header=True, index=False)
