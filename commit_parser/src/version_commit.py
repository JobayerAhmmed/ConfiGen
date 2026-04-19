import logging

import git
import pandas as pd

from config import temp_dir
from utils import clone_repo
from utils import checkout_to_commit
from utils import read_csv_to_df


def generate_version_commit_ids(project_config):
    """Collects tag names and commit ids for a subject and
    store in a csv file."""
    logging.info('[{}] Getting commit ids for versions...'.format(
        project_config.project_name))
    tag_separator_org = '.'
    tag_separator_new = '.'
    tag_prefix = ''
    version_start = 0
    version_end = 0
    major_start, major_end = 1, 1
    minor_start, minor_end = 0, 0
    patch_start, patch_end = 0, 0

    if project_config.project_dir_name == 'busybox':
        tag_separator_org = '_'
        version_start = 140
        version_end = 1361
        major_start, major_end = 1, 1
        minor_start, minor_end = 4, 36
        patch_start, patch_end = -1, -1 # -1 means it's range is not fixed
    elif project_config.project_dir_name == 'uclibc-ng':
        tag_prefix = 'v'
        version_start = 100
        version_end = 1045
        major_start, major_end = 1, 1
        minor_start, minor_end = 0, 0
        patch_start, patch_end = 0, 45
    elif project_config.project_dir_name == 'toybox':
        version_start = 2
        version_end = 810
        major_start, major_end = 0, 0
        minor_start, minor_end = 0, 8
        patch_start, patch_end = -1, 10
    else:
        logging.error('Error: unknown project dir name: {}'
            .format(project_config.project_dir_name))

    ret_value = clone_repo(project_config.repo_url,
                           project_config.project_repo_dir, temp_dir)
    if ret_value == -1:
        return
    ret_value = checkout_to_commit(project_config, project_config.repo_branch)
    if ret_value == -1:
        logging.error('[{}] Failed to checkout to {}'
                      .format(project_config.project_name,
                              project_config.repo_branch))
        return

    repo = git.Repo(project_config.project_repo_dir)
    tags = repo.tags
    versions = []
    for tag in tags:
        commit_id = tag.commit.hexsha
        year = tag.commit.committed_datetime.year
        tag_name = tag.name
        if tag_prefix:
            tag_name = tag_name.lstrip(tag_prefix)
        parts = tag_name.split(tag_separator_org)
        if len(parts) < 3:
            continue
        all_parts_digit = True
        for p in parts:
            if not p.isdigit():
                all_parts_digit = False
                break
        if not all_parts_digit:
            continue
        try:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])
            forth = -1
            version_value = (100 * major) + (10 * minor) + (1 * patch)
            if len(parts) > 3:
                forth = int(parts[3])
                version_value += (0.1 * forth)
        except ValueError:
            logging.error(f'Error: {tag.name} contains invalid int parts')
            version_value = -1
        if version_value == -1:
            continue
        if major_end != -1 and (major > major_end or major < major_start):
            continue
        if minor_end != -1 and (minor > minor_end or minor < minor_start):
            continue
        if patch_end != -1 and (patch > patch_end or patch < patch_start):
            continue
        if version_value > version_end or version_value < version_start:
            continue
        new_tag_name = f"{major}{tag_separator_new}{minor}{tag_separator_new}{patch}"
        if forth != -1:
            new_tag_name = f"{major}{tag_separator_new}{minor}{tag_separator_new}{patch}{tag_separator_new}{forth}"
        tag_commit = {'value': version_value, 'tag': new_tag_name,
                      'sha': commit_id, 'year': year}
        versions.append(tag_commit)
    sorted_versions = sorted(versions, key=lambda k: k['value'],
                             reverse=True)
    
    df = pd.DataFrame(sorted_versions)
    df = df[['tag', 'sha', 'year']]

    df['gen_config_cmd'] = ''
    df['config_entry_file'] = 'Config.in'
    df['config_issues'] = [[] for _ in range(len(df))]

    # 
    # Update gen_config_cmd,config_entry_file fields from doc_gen_status file
    # 
    doc_gen_df = read_csv_to_df(project_config.file_commit_ids_doc_gen_status)
    for index, row in df.iterrows():
        rows = doc_gen_df[doc_gen_df['sha'] == row['sha']]
        if not rows.empty:
            df.at[index, 'gen_config_cmd'] = rows['gen_config_cmd'].values[0]
            df.at[index, 'config_entry_file'] = rows['config_entry_file'].values[0]

    # 
    # Update config_issues field from config_issues.csv file
    # 
    config_issues_df = read_csv_to_df(project_config.file_config_issues)
    for index, row in df.iterrows():
        rows = config_issues_df[config_issues_df['sha'] == row['sha']]
        if not rows.empty:
            df.at[index, 'config_issues'] = rows['config_issues'].values[0]

    if project_config.project_dir_name == 'busybox':
        # till 1.17.0, gen_config_cmd = scripts/gen_build_files.sh . .
        row_1170 = df.index[df['sha'] == 'b2d95147c989448f23cc59c63b83e2d89f0bd9cd'].tolist()
        if len(row_1170) > 0:
            df.loc[0: row_1170[0], 'gen_config_cmd'] = 'scripts/gen_build_files.sh . .'
            # df.loc[alpha_start[0]: alpha_end[0],
                #    'config_entry_file'] = 'extra/Configs/Config.alpha'
        # df.loc[df['sha'] == '1a64f6a20aaf6ea4dbba68bbfa8cc1ab7e5c57c4', 'gen_config_cmd'] = 'scripts/gen_build_files.sh . .'
    elif project_config.project_dir_name == 'uclibc-ng':
        df.loc[df['sha'] == '9a4636f2d3f7ee7de34211a6d45201e328d84e48',
               'config_entry_file'] = 'extra/Configs/Config.in'
    elif project_config.project_dir_name == 'toybox':
        df.loc[df['sha'] == '344c267e9fe5c6a39efdbf0305bd873d5bef65f3', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'a62df5f6da8e52fca695cff0bdbc3dd2e5228238', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == '90e421392a997c9acad7d2351bac721a31d8dae3', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'aa7f3faa2c42ab829c200cb8048a0fa8743c9290', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'e7a169ba2ca710e8fb602dd49006cfd201293018', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'd9ee848acd51149c93176d8e5364b30ce8248e34', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'fe0f3d5fa93b85a43854953b5997ad802fbad4a2', 'gen_config_cmd'] = 'scripts/genconfig.sh'
        df.loc[df['sha'] == 'a95475bf83d9d57d1f9d9d42f006d8161455ef0b', 'gen_config_cmd'] = 'scripts/genconfig.sh'

    df.to_csv(project_config.file_commit_ids_versions, header=True, index=False)
    ret_value = clone_repo(project_config.repo_url,
                           project_config.project_repo_dir, temp_dir)
