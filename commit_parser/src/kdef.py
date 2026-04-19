"""Process git commit history and categorize changes
of files and Kconfig symbols."""

import os
import io
import ast
import subprocess
import copy
import logging
import fnmatch
import logging

import pandas as pd
from git import Repo
import progressbar

from utils import *



def run_kdef(project_config):
    gen_commit_data_files_by_change_type(project_config)
    gen_kdef_modification_per_commit(project_config)
    gen_kdef_count_change_type(project_config)
    kdef_add_count_per_commit(project_config)
    kdef_del_count_per_commit(project_config)
    kdef_add_del_count_per_commit(project_config)
    gen_commit_ids_add_del_kdef(project_config)

    pass


def gen_commit_data_files_by_change_type(project_config):
    """Generate files based on change types in commit data.
    Files:
        kdef_commits.csv
        code_commits.csv
        kdef_code_commits.csv
        other_commits.csv
        no_change_commits.csv
    """
    logging.info('[{}] Generating csv files of change types from commit data...'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_commit_data)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])
    df['files'] = df['files'].apply(ast.literal_eval) # convert string to list

    # {
    #     sha,
    #     commit.committer.date,
    #     files: [{filename, status, kconf_def_change, code_change,
    #              other_change, no_change}]
    # }
    result = []
    bar = progressbar.ProgressBar(max_value=len(df), redirect_stdout=True).start()
    for index, row in df.iterrows():
        res_row = {'sha': row['sha'],
                   'commit.committer.date': row['commit.committer.date'],
                   'files': []}
        for file in row['files']:
            filename: str = file['filename']
            filename_after_last_slash = os.path.basename(filename)
            status = file['status']
            patch = file['patch']
            res_file = {'filename': filename, 'status': status, 
                        'kconf_def_change': False, 'code_change': False,
                        'other_change': False, 'no_change': False}
            # status in ["modified", "added", "removed", "renamed"]:
            patch = patch.decode(encoding='utf-8', errors='ignore')
            patch = patch.strip()

            is_source_file = False
            for i in range(len(project_config.source_file_pattern)):
                if fnmatch.fnmatchcase(filename_after_last_slash,
                                        project_config.source_file_pattern[i]):
                    is_source_file = True
                    break
            is_config_file = False
            for i in range(len(project_config.config_file_pattern)):
                if fnmatch.fnmatchcase(filename_after_last_slash,
                                        project_config.config_file_pattern[i]):
                    is_config_file = True
                    break

            patch_lines = patch.split("\n")
            if is_source_file:
                if patch == '':
                    res_file['no_change'] = True
                elif project_config.project_dir_name == 'toybox':
                    res_file['kconf_def_change'], res_file['code_change'] = \
                        check_change_type_toybox(project_config, row['sha'],
                                                    filename, patch_lines)
                else:
                    # Checking kdef_start is enough for all
                    if project_config.kdef_start is not None:
                        for line in patch_lines:
                            if line.startswith('+'):
                                if (project_config.kdef_edit_plus.match(line)
                                    or project_config.kdef_add.match(line)):
                                    res_file['kconf_def_change'] = True
                                    break
                            elif line.startswith('-'):
                                if (project_config.kdef_edit_minus.match(line)
                                    or project_config.kdef_del.match(line)):
                                    res_file['kconf_def_change'] = True
                                    break
                        for line in patch_lines:
                            if line.startswith('+'):
                                if not (project_config.kdef_edit_plus.match(line)
                                        or project_config.kdef_add.match(line)):
                                    res_file['code_change'] = True
                                    break
                            elif line.startswith('-'):
                                if not (project_config.kdef_edit_minus.match(line)
                                        or project_config.kdef_del.match(line)):
                                    res_file['code_change'] = True
                                    break
                    else: # uclibc has no kdef in source code files
                        res_file['code_change'] = True
                        
                if (not res_file['kconf_def_change']
                    and not res_file['code_change']):
                    res_file['no_change'] = True
            elif is_config_file:
                res_file['kconf_def_change'] = any(line.startswith('+')
                                                    or line.startswith('-')
                                                    for line in patch_lines)
                if not res_file['kconf_def_change']:
                    res_file['no_change'] = True
            else:
                res_file['other_change'] = True
            res_row['files'].append(copy.deepcopy(res_file))
        result.append(copy.deepcopy(res_row))
        bar.update(index + 1)
    bar.finish()
    
    res_df = pd.DataFrame(result)

    kconf_def_commits = []
    code_commits = []
    kconf_code_commits = []
    other_commits = []
    no_change_commits = []

    for i, files in enumerate(res_df['files']):
        kconf_files = sum(1 for file in files if file['kconf_def_change'])
        code_files = sum(1 for file in files if file['code_change'])
        other_files = sum(1 for file in files if file['other_change'])
        if kconf_files > 0:
            if code_files > 0:
                kconf_code_commits.append(i)
            else:
                kconf_def_commits.append(i)
        else:
            if code_files > 0:
                code_commits.append(i)
            elif other_files > 0:
                other_commits.append(i)
            else:
                no_change_commits.append(i)

    kconf_def_commits = res_df.iloc[kconf_def_commits]
    code_commits = res_df.iloc[code_commits]
    kconf_code_commits = res_df.iloc[kconf_code_commits]
    other_commits = res_df.iloc[other_commits]
    no_change_commits = res_df.iloc[no_change_commits]

    kconf_def_commits.to_csv(project_config.file_kdef_commits, header=True,
                             index=False)
    code_commits.to_csv(project_config.file_code_commits, header=True,
                        index=False)
    kconf_code_commits.to_csv(project_config.file_kdef_code_commits,
                              header=True, index=False)
    other_commits.to_csv(project_config.file_other_commits, header=True,
                         index=False)
    no_change_commits.to_csv(project_config.file_no_change_commits,
                             header=True, index=False)

    total_commit_count = (kconf_def_commits.shape[0] + code_commits.shape[0]
                          + kconf_code_commits.shape[0] + other_commits.shape[0]
                          + no_change_commits.shape[0])
    assert df.shape[0] == total_commit_count, (str(df.shape[0]) + " != "
                                               + str(total_commit_count))


def check_change_type_toybox(project_config, commit_id, filename, patch_lines):
    kdef_change = False
    code_change = False
    
    # Deleted file cannot be found in commit tree.
    # So, remove - from patch lines and use those as file lines.
    if len(patch_lines) > 0 and patch_lines[0].endswith('+0,0 @@'):
        file_lines = [line[1:] for line in patch_lines]
        code_change = True
        for line in file_lines:
            if project_config.kdef_start.match(line):
                kdef_change = True
                break
        return kdef_change, code_change
    
    repo = Repo(project_config.project_repo_dir)
    commit = repo.commit(commit_id)
    file_blob = commit.tree / filename
    with io.BytesIO(file_blob.data_stream.read()) as f:
        file_lines = f.read().decode(encoding='utf-8', errors='ignore')
    file_lines = file_lines.split('\n')

    config_start_line = -1
    config_end_line = -1
    for i, line in enumerate(file_lines):
        if project_config.kdef_start.match(line):
            config_start_line = i
            break
    for i in range(max(0, config_start_line), len(file_lines)):
        if file_lines[i].strip().startswith('*/'):
            config_end_line = i - 1
            break

    if config_start_line == -1 or config_end_line == -1:
        # Check if a config is deleted
        for line in patch_lines:
            if project_config.kdef_del.match(line):
                kdef_change = True
                break
        if not kdef_change:
            code_change = True
            return kdef_change, code_change

    patch_i = 0
    common_i = 0
    diff_start = 0
    while patch_i < len(patch_lines):
        line = patch_lines[patch_i]
        if line.startswith('@@ -'):
            diff_range = line.split('@@')[1].strip().split()[1].split(',')
            diff_start = int(diff_range[0]) - 1
            patch_i += 1
            common_i = 0
        elif line[0] == '+':
            file_i = diff_start + common_i - 1
            patch_i += 1
            common_i += 1
            if (project_config.kdef_add 
                and project_config.kdef_add.match(line)):
                kdef_change = True
            else:
                if file_i < config_start_line:
                    code_change = True
                elif file_i > config_end_line:
                    code_change = True
                    return kdef_change, code_change
                else:
                    kdef_change = True
        elif line[0] == '-':
            file_i = diff_start + common_i - 1
            patch_i += 1
            if (project_config.kdef_del 
                and project_config.kdef_del.match(line)):
                kdef_change = True
            else:
                if file_i < config_start_line:
                    code_change = True
                elif file_i > config_end_line:
                    code_change = True
                    return kdef_change, code_change
                else:
                    kdef_change = True
        else: # line[0] == ' '
            patch_i += 1
            common_i += 1
    return kdef_change, code_change

    
def gen_kdef_modification_per_commit(project_config):
    logging.info('[{}] Generating file kdef.csv with Kconfig symbol modification...'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_commit_data)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])

    start_row = df[df['sha'] == project_config.start_commit_id].index[0] + 1
    df = df[start_row : ]
    df = df.reset_index(drop=True)
    df['files'] = df['files'].apply(ast.literal_eval) # convert string to list

    repo = Repo(project_config.project_repo_dir)

    # {
    #     sha,
    #     commit.committer.date,
    #     files: [{filename, status, defs_add:[], defs_del:[], defs_edit:[],
    #              only_add:[], only_del:[], del_add:[]}],
    #     defs_move: []
    # }
    result = []
    bar = progressbar.ProgressBar(max_value=len(df), redirect_stdout=True).start()
    for index, row in df.iterrows():
        res_row = {'sha': row['sha'],
                   'commit.committer.date': row['commit.committer.date'],
                   'files': []}
        for file in row['files']:
            filename = file['filename']
            filename_after_last_slash = os.path.basename(filename)
            status = file['status']
            patch = file['patch']
            res_file = {'filename': filename, 'status': status, 
                        'defs_add': [], 'defs_del': [], 'defs_edit': []}
            
            is_source_file = False
            for i in range(len(project_config.source_file_pattern)):
                if fnmatch.fnmatchcase(filename_after_last_slash,
                                       project_config.source_file_pattern[i]):
                    is_source_file = True
                    break
            is_config_file = False
            for i in range(len(project_config.config_file_pattern)):
                if fnmatch.fnmatchcase(filename_after_last_slash,
                                       project_config.config_file_pattern[i]):
                    is_config_file = True
                    break
                
            patch = patch.decode(encoding='utf-8', errors='ignore')
            patch = patch.strip()
            patch_lines = patch.split("\n")
            if is_source_file:
                if status == "modified" or status == "renamed":
                    if patch == '':
                        continue
                    commit = repo.commit(row['sha'])
                    file_blob = commit.tree / filename
                    with io.BytesIO(file_blob.data_stream.read()) as f:
                        file_lines = f.read().decode(encoding='utf-8',
                                                    errors='ignore')
                    file_lines = file_lines.split('\n')

                    if project_config.project_dir_name == 'toybox':
                        check_kdef_modification_toybox(project_config,
                                                       file_lines, patch_lines,
                                                       res_file)
                    else:
                        patch_i = 0 # index for patch lines
                        common_i = 0 # index for file and patch lines
                        diff_start = 0
                        while patch_i < len(patch_lines):
                            if len(patch_lines[patch_i]) < 3:
                                patch_i += 1
                                common_i += 1
                                continue
                            # Sometimes, there might be spaces before //config:
                            # patch_lines[0] is +, - or space
                            if patch_lines[patch_i].startswith('@@ -'):
                                diff_range = patch_lines[patch_i].split('@@')[1].strip().split()[1].split(',')
                                diff_start = int(diff_range[0]) - 1
                                patch_i += 1
                                common_i = 0
                            elif (project_config.kdef_add 
                                  and (m := project_config.kdef_add.match(patch_lines[patch_i]))):
                                symbol = m.group(1)
                                res_file['defs_add'].append(symbol)
                                patch_i += 1
                                common_i += 1
                                # + or - lines belong to the added symbol.
                                # So, skip patch lines for the next +, - lines.
                                while patch_i < len(patch_lines):
                                    if project_config.kdef_edit_plus.match(patch_lines[patch_i]):
                                        patch_i += 1
                                        common_i += 1
                                    elif project_config.kdef_edit_minus.match(patch_lines[patch_i]):
                                        patch_i += 1
                                    else:
                                        break
                            elif (project_config.kdef_del
                                  and (m := project_config.kdef_del.match(patch_lines[patch_i]))):
                                symbol = m.group(1)
                                res_file['defs_del'].append(symbol)
                                patch_i += 1
                                # - lines belong to the deleted symbol.
                                # So, skip patch lines for the next - lines.
                                # + lines belong to an existing symbol.
                                # So, edited symbol is searched from file lines.
                                while patch_i < len(patch_lines):
                                    if project_config.kdef_edit_minus.match(patch_lines[patch_i]):
                                        patch_i += 1
                                    else:
                                        break
                            elif patch_lines[patch_i][0] == '-':
                                if (project_config.kdef_edit_minus
                                    and project_config.kdef_edit_minus.match(patch_lines[patch_i])):
                                    # Find start of symbol in file lines
                                    file_i = diff_start + common_i - 1
                                    symbol = None
                                    while (file_i >= 0
                                           and project_config.kdef_body.match(file_lines[file_i])):
                                        file_i -= 1
                                    if (file_i > -1
                                        and (m := project_config.kdef_start.match(file_lines[file_i]))):
                                        symbol = m.group(1)
                                        res_file['defs_edit'].append(symbol)
                                    # Find end of symbol in patch lines
                                    patch_i += 1
                                    while patch_i < len(patch_lines):
                                        if project_config.kdef_edit_minus.match(patch_lines[patch_i]):
                                            patch_i += 1
                                        elif (project_config.kdef_edit_plus.match(patch_lines[patch_i])
                                              or project_config.kdef_body.match(patch_lines[patch_i])):
                                            patch_i += 1
                                            common_i += 1
                                        else:
                                            break
                                else:
                                    patch_i += 1
                            elif patch_lines[patch_i][0] == '+':
                                if (project_config.kdef_edit_plus
                                    and project_config.kdef_edit_plus.match(patch_lines[patch_i])):
                                    # Find start of symbol in file lines
                                    file_i = diff_start + common_i
                                    symbol = None
                                    while (file_i >= 0
                                           and project_config.kdef_body.match(file_lines[file_i])):
                                        file_i -= 1
                                    if (file_i > -1
                                        and (m := project_config.kdef_start.match(file_lines[file_i]))):
                                        symbol = m.group(1)
                                        res_file['defs_edit'].append(symbol)
                                    # Find end of symbol in patch
                                    patch_i += 1
                                    common_i += 1
                                    while patch_i < len(patch_lines):
                                        if project_config.kdef_edit_minus.match(patch_lines[patch_i]):
                                            patch_i += 1
                                        elif (project_config.kdef_edit_plus.match(patch_lines[patch_i])
                                              or project_config.kdef_body.match(patch_lines[patch_i])):
                                            patch_i += 1
                                            common_i += 1
                                        else:
                                            break
                                else:
                                    patch_i += 1
                                    common_i += 1
                            else:
                                patch_i += 1
                                common_i += 1
                elif status == "added":
                    if project_config.kdef_add:
                        for line in patch_lines:
                            if m := project_config.kdef_add.match(line):
                                symbol = m.group(1)
                                res_file['defs_add'].append(symbol)
                elif status == "removed":
                    if project_config.kdef_del:
                        for line in patch_lines:
                            if m := project_config.kdef_del.match(line):
                                symbol = m.group(1)
                                res_file['defs_del'].append(symbol)
            elif is_config_file:
                if status == "modified" or status == "renamed":
                    if patch == '':
                        continue
                    commit = repo.commit(row['sha'])
                    file_blob = commit.tree / filename
                    with io.BytesIO(file_blob.data_stream.read()) as f:
                        file_lines = f.read().decode(encoding='utf-8', errors='ignore')
                    file_lines = file_lines.split('\n')

                    patch_i = 0 # index for patch lines
                    common_i = 0 # index for file and patch lines
                    diff_start = 0
                    while patch_i < len(patch_lines):
                        if len(patch_lines[patch_i]) < 1:
                            patch_i += 1
                            common_i += 1
                            continue
                        if patch_lines[patch_i].startswith('@@ -'):
                            diff_range = patch_lines[patch_i].split('@@')[1].strip().split()[1].split(',')
                            diff_start = int(diff_range[0]) - 1
                            patch_i += 1
                            common_i = 0
                        elif (project_config.kdef_in_src_add
                              and (m := project_config.kdef_in_src_add.match(patch_lines[patch_i]))):
                            symbol = m.group(1)
                            res_file['defs_add'].append(symbol)
                            patch_i += 1
                            common_i += 1
                            # + or - lines belong to the added symbol.
                            # So, skip patch lines for the next +, - lines.
                            while patch_i < len(patch_lines):
                                if (project_config.kdef_in_src_edit_plus.match(patch_lines[patch_i])
                                    or patch_lines[patch_i].strip() == '+'):
                                    patch_i += 1
                                    common_i += 1
                                elif (project_config.kdef_in_src_edit_minus.match(patch_lines[patch_i])
                                      or patch_lines[patch_i].strip() == '-'):
                                    patch_i += 1
                                else:
                                    break
                        elif (project_config.kdef_in_src_del
                              and (m := project_config.kdef_in_src_del.match(patch_lines[patch_i]))):
                            symbol = m.group(1)
                            res_file['defs_del'].append(symbol)
                            patch_i += 1
                            # - lines belong to the deleted symbol.
                            # So, skip patch lines for the next - lines.
                            # + lines belong to an existing symbol.
                            # So, edited symbol is searched from file lines.
                            while patch_i < len(patch_lines):
                                if (project_config.kdef_in_src_edit_minus.match(patch_lines[patch_i])
                                    or patch_lines[patch_i].strip() == '-'):
                                    patch_i += 1
                                else:
                                    break
                        elif patch_lines[patch_i][0] == '-':
                            # If line is not indent with \t, then
                            # that change is not of a config, it might
                            # be for comments or others
                            if (project_config.kdef_in_src_edit_minus
                                and project_config.kdef_in_src_edit_minus.match(patch_lines[patch_i])):
                                # Find start of symbol in file lines
                                file_i = diff_start + common_i - 1
                                symbol = None
                                while (file_i >= 0
                                       and project_config.kdef_in_src_body.match(file_lines[file_i])):
                                    file_i -= 1
                                if (file_i > -1
                                    and (m := project_config.kdef_in_src_start.match(file_lines[file_i]))):
                                    symbol = m.group(1)
                                    res_file['defs_edit'].append(symbol)
                                # Find end of symbol in patch lines
                                patch_i += 1
                                while patch_i < len(patch_lines):
                                    if (project_config.kdef_in_src_edit_minus.match(patch_lines[patch_i])
                                        or patch_lines[patch_i].strip() == '-'):
                                        patch_i += 1
                                    elif (project_config.kdef_in_src_edit_plus.match(patch_lines[patch_i])
                                          or patch_lines[patch_i].strip() == '+'
                                          or project_config.kdef_in_src_body.match(patch_lines[patch_i])):
                                        patch_i += 1
                                        common_i += 1
                                    else:
                                        break
                            else:
                                patch_i += 1
                            # No j += 1, because for deleted line in patch,
                            # line number does not increase in original file.
                        elif patch_lines[patch_i][0] == '+':
                            if (project_config.kdef_in_src_edit_plus
                                and project_config.kdef_in_src_edit_plus.match(patch_lines[patch_i])):
                                # Find start of symbol in file lines
                                file_i = diff_start + common_i
                                symbol = None
                                while (file_i >= 0
                                       and project_config.kdef_in_src_body.match(file_lines[file_i])):
                                    file_i -= 1
                                if (file_i > -1
                                    and (m := project_config.kdef_in_src_start.match(file_lines[file_i]))):
                                    symbol = m.group(1)
                                    res_file['defs_edit'].append(symbol)
                                # Find end of symbol in patch lines
                                patch_i += 1
                                common_i += 1
                                while patch_i < len(patch_lines):
                                    if (project_config.kdef_in_src_edit_minus.match(patch_lines[patch_i])
                                        or patch_lines[patch_i].strip() == '-'):
                                        patch_i += 1
                                    elif (project_config.kdef_in_src_edit_plus.match(patch_lines[patch_i])
                                          or patch_lines[patch_i].strip() == '+'
                                          or project_config.kdef_in_src_body.match(patch_lines[patch_i])):
                                        patch_i += 1
                                        common_i += 1
                                    else:
                                        break
                            else:
                                patch_i += 1
                                common_i += 1
                        else:
                            patch_i += 1
                            common_i += 1
                elif status == "added":
                    if project_config.kdef_in_src_add:
                        for line in patch_lines:
                            if m := project_config.kdef_in_src_add.match(line):
                                symbol = m.group(1)
                                res_file['defs_add'].append(symbol)
                elif status == "removed":
                    if project_config.kdef_in_src_del:
                        for line in patch_lines:
                            if m := project_config.kdef_in_src_del.match(line):
                                symbol = m.group(1)
                                res_file['defs_del'].append(symbol)
            
            res_file['defs_add'] = remove_duplicates(res_file['defs_add'])
            res_file['defs_del'] = remove_duplicates(res_file['defs_del'])
            res_file['defs_edit'] = remove_duplicates(res_file['defs_edit'])

            # Discard items from edit if they exist in add or del
            res_file['defs_edit'] = [item for item in res_file['defs_edit']
                                     if item not in res_file['defs_add']
                                     and item not in res_file['defs_del']]

            if (len(res_file['defs_add']) > 0 or len(res_file['defs_del']) > 0
                or len(res_file['defs_edit']) > 0):
                res_row['files'].append(copy.deepcopy(res_file))
        is_add_del_edit = (len(res_row['files']) > 0
                           and any(len(file['defs_add']) > 0
                                   or len(file['defs_del'])
                                   or len(file['defs_edit']) > 0
                                   for file in res_row['files']))
        if is_add_del_edit:
            result.append(copy.deepcopy(res_row))
        bar.update(index + 1)
    bar.finish()
    
    df = pd.DataFrame(result)

    # Check any add or delete is also present as edit
    # for index, row in df.iterrows():
    #     msg = ''
    #     for file in row['files']:
    #         add_in_edit = [item for item in file['defs_add']
    #                        if item in file['defs_edit']]
    #         del_in_edit = [item for item in file['defs_del']
    #                        if item in file['defs_edit']]
    #         if len(add_in_edit) > 0 or len(del_in_edit) > 0:
    #             msg += ("\n" + file['filename'] + ": add in edit: "
    #                     + ','.join(add_in_edit) + ", del in edit: "
    #                     + ','.join(del_in_edit))
    #     if len(msg) > 0:
    #         logging.info(row['sha'] + msg)

    # Separate as only add, only delete, delete & add, moved
    df['defs_move'] = [[] for _ in range(df.shape[0])]
    for index, row in df.iterrows():
        for file in row['files']:
            file['only_add'] = [item for item in file['defs_add']
                                if item not in file['defs_del']]
            file['only_del'] = [item for item in file['defs_del']
                                if item not in file['defs_add']]
            file['del_add'] = [item for item in file['defs_add']
                               if item in file['defs_del']]
        # Find moved Kconfig defs
        for patch_i, file in enumerate(row['files']):
            other_files = [x for j, x in enumerate(row['files'])
                           if j != patch_i]
            for kdef in file['only_del']:
                for o_file in other_files:
                    if kdef in o_file['only_add']:
                        df.at[index,'defs_move'].append(kdef)
        # Remove defs_move items from only_add and only_del
        for file in row['files']:
            file['only_add'] = [item for item in file['only_add']
                                if item not in df.at[index,'defs_move']]
            file['only_del'] = [item for item in file['only_del']
                                if item not in df.at[index,'defs_move']]
    df.to_csv(project_config.file_kdef, header=True, index=False)


def check_kdef_modification_toybox(project_config, file_lines, patch_lines,
                                   res_file):
    kdef_start_line = -1
    kdef_end_line = -1
    for i, line in enumerate(file_lines):
        if project_config.kdef_start.match(line):
            kdef_start_line = i
            break
    if kdef_start_line == -1:
        return
    for i in range(kdef_start_line, len(file_lines)):
        if file_lines[i].strip().startswith('*/'):
            kdef_end_line = i - 1
            break

    patch_i = 0 # index for patch lines
    common_i = 0 # index for file and patch lines
    diff_start = 0
    while patch_i < len(patch_lines):
        if len(patch_lines[patch_i]) < 1:
            patch_i += 1
            common_i += 1
            continue
        if patch_lines[patch_i].startswith('@@ -'):
            diff_range = patch_lines[patch_i].split('@@')[1].strip().split()[1].split(',')
            diff_start = int(diff_range[0]) - 1
            patch_i += 1
            common_i = 0
        elif (project_config.kdef_add
              and (m := project_config.kdef_add.match(patch_lines[patch_i]))):
            symbol = m.group(1)
            res_file['defs_add'].append(symbol)
            patch_i += 1
            common_i += 1
            # + or - lines belong to the added symbol.
            # So, skip patch lines for the next +, - lines.
            while patch_i < len(patch_lines):
                if (project_config.kdef_edit_plus.match(patch_lines[patch_i])
                    or patch_lines[patch_i].strip() == '+'):
                    patch_i += 1
                    common_i += 1
                elif (project_config.kdef_edit_minus.match(patch_lines[patch_i])
                      or patch_lines[patch_i].strip() == '-'):
                    patch_i += 1
                else:
                    break
        elif (project_config.kdef_del
              and (m := project_config.kdef_del.match(patch_lines[patch_i]))):
            symbol = m.group(1)
            res_file['defs_del'].append(symbol)
            patch_i += 1
            # - lines belong to the deleted symbol.
            # So, skip patch lines for the next - lines.
            # + lines belong to an existing symbol.
            # So, edited symbol is searched from file lines.
            while patch_i < len(patch_lines):
                if (project_config.kdef_edit_minus.match(patch_lines[patch_i])
                    or patch_lines[patch_i].strip() == '-'):
                    patch_i += 1
                else:
                    break
        elif patch_lines[patch_i][0] == '-':
            if (project_config.kdef_edit_minus
                and project_config.kdef_edit_minus.match(patch_lines[patch_i])):
                file_i = diff_start + common_i - 1
                if file_i >= kdef_start_line:
                    if file_i <= kdef_end_line:
                        # Find start of symbol in file lines
                        symbol = None
                        while (file_i >= 0
                               and project_config.kdef_body.match(file_lines[file_i])):
                            file_i -= 1
                        if (file_i > -1
                            and (m := project_config.kdef_start.match(file_lines[file_i]))):
                            symbol = m.group(1)
                            res_file['defs_edit'].append(symbol)
                        # Find end of symbol in patch lines
                        patch_i += 1
                        while patch_i < len(patch_lines):
                            if (project_config.kdef_edit_minus.match(patch_lines[patch_i])
                                or patch_lines[patch_i].strip() == '-'):
                                patch_i += 1
                            elif (project_config.kdef_edit_plus.match(patch_lines[patch_i])
                                  or patch_lines[patch_i].strip() == '+'
                                  or project_config.kdef_body.match(patch_lines[patch_i])):
                                patch_i += 1
                                common_i += 1
                            else:
                                break
                    else:
                        patch_i = len(patch_lines)
                else:
                    patch_i += 1
            else:
                patch_i += 1
        elif patch_lines[patch_i][0] == '+':
            if (project_config.kdef_edit_plus
                and project_config.kdef_edit_plus.match(patch_lines[patch_i])):
                file_i = diff_start + common_i
                if file_i >= kdef_start_line:
                    if file_i <= kdef_end_line:
                        # Find start of symbol in file lines
                        symbol = None
                        while (file_i >= 0
                               and project_config.kdef_body.match(file_lines[file_i])):
                            file_i -= 1
                        if (file_i > -1
                            and (m := project_config.kdef_start.match(file_lines[file_i]))):
                            symbol = m.group(1)
                            res_file['defs_edit'].append(symbol)
                        # Find end of symbol in patch lines
                        patch_i += 1
                        common_i += 1
                        while patch_i < len(patch_lines):
                            if (project_config.kdef_edit_minus.match(patch_lines[patch_i])
                                or patch_lines[patch_i].strip() == '-'):
                                patch_i += 1
                            elif (project_config.kdef_edit_plus.match(patch_lines[patch_i])
                                  or patch_lines[patch_i].strip() == '+'
                                  or project_config.kdef_body.match(patch_lines[patch_i])):
                                patch_i += 1
                                common_i += 1
                            else:
                                break
                    else:
                        patch_i = len(patch_lines)
                else:
                    patch_i += 1
                    common_i += 1
            else:
                patch_i += 1
                common_i += 1
        else:
            patch_i += 1
            common_i += 1
            

def remove_duplicates(data):
    seen = set()
    result = []
    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def gen_kdef_count_change_type(project_config):
    logging.info("[{}] Generating Kconfig symbol modification count per commit..."
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_kdef)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])

    df['files'] = df['files'].apply(ast.literal_eval) # convert string to list
    df['defs_move'] = df['defs_move'].apply(ast.literal_eval)

    result = []
    for _, row in df.iterrows():
        only_add = [file['only_add'] for file in row['files']]
        only_del = [file['only_del'] for file in row['files']]
        del_add = [file['del_add'] for file in row['files']]
        defs_edit = [file['defs_edit'] for file in row['files']]

        only_add = [item for sublist in only_add for item in sublist]
        only_del = [item for sublist in only_del for item in sublist]
        del_add = [item for sublist in del_add for item in sublist]
        defs_edit = [item for sublist in defs_edit for item in sublist]

        result.append({'sha': row['sha'],
                       'commit.committer.date': row['commit.committer.date'], 
                       'only_add_count': len(only_add),
                       'only_del_count': len(only_del),
                       'del_add_count': len(del_add),
                       'defs_edit_count': len(defs_edit),
                       'defs_move_count': len(row['defs_move']),
                       'only_add': only_add,
                       'only_del': only_del,
                       'del_add': del_add, 
                       'defs_edit': defs_edit,
                       'defs_move': row['defs_move']})
        # Check uniqueness
        # if len(only_add) != len(list(set(only_add))):
        #     print('Not unique only_add for', row['sha'])
        #     print(sorted(only_add))
        #     print(sorted(list(set(only_add))))
        # if len(only_del) != len(list(set(only_del))):
        #     print('Not unique only_del for', row['sha'])
        #     print(sorted(only_del))
        #     print(sorted(list(set(only_del))))
        # if len(del_add) != len(list(set(del_add))):
        #     print('Not unique del_add for', row['sha'])
        #     print(sorted(del_add))
        #     print(sorted(list(set(del_add))))
        # if len(defs_edit) != len(list(set(defs_edit))):
        #     print('Not unique defs_edit for', row['sha'])
        #     print(sorted(defs_edit))
        #     print(sorted(list(set(defs_edit))))
        # if len(row['defs_move']) != len(list(set(row['defs_move']))):
        #     print('Not unique defs_move for', row['sha'])
        #     print(sorted(row['defs_move']))
        #     print(sorted(list(set(row['defs_move']))))
    result_df = pd.DataFrame(result)
    result_df.to_csv(project_config.file_kdef_count_change_type, header=True,
                     index=False)


def gen_commit_ids_add_del_kdef(project_config):
    """Extract commit ids that have add and/or delete kconfig definition.
    Since kdef is considered after commit config_prefix_start_commit_id,
    add_del_kdef commit ids are taken after config_prefix_start_commit_id.
    """
    logging.info("[{}] Generating file commit_ids_add_del_kdef.csv"
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_kdef)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])

    list_config_prefix_start = df[df['sha'] == project_config
                                  .config_prefix_start_commit_id].index.tolist()
    if len(list_config_prefix_start) > 0:
        df = df[list_config_prefix_start[0] : ]
        df = df.reset_index(drop=True)

    df['files'] = df['files'].apply(ast.literal_eval)

    commit_ids = []
    for _, row in df.iterrows():
        if any((len(file['only_add']) > 0 or len(file['only_del']) > 0)
               for file in row['files']):
            commit_ids.append({'sha': row['sha'],
                               'commit.committer.date': row['commit.committer.date']})

    df = pd.DataFrame(commit_ids)
    df.to_csv(project_config.file_commit_ids_add_del_kdef, header=True,
              index=False)


def kdef_add_count_per_commit(project_config):
    logging.info('[{}] Generating Kconfig symbol add count per commit...'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_kdef_count_change_type)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])
    df['only_add'] = df['only_add'].apply(ast.literal_eval)

    result = []
    for _, row in df.iterrows():
        if row['only_add_count'] > 0:
            result.append({'sha': row['sha'], 
                           'commit.committer.date': row['commit.committer.date'],
                           'only_add_count': row['only_add_count'], 
                           'only_add': row['only_add']})
    df = pd.DataFrame(result)

    # Calculate time distance between add commits
    df['time_distance'] = 0
    for i in range(1, df.shape[0]):
        df.at[i, 'time_distance'] = (df.iloc[i]['commit.committer.date']
                                     - df.iloc[i-1]['commit.committer.date']
                                     ).total_seconds()
    df = df[['sha','commit.committer.date','only_add_count','time_distance',
             'only_add']]
    df.to_csv(project_config.file_kdef_add_count_per_commit,
              header=True, index=False)


def kdef_del_count_per_commit(project_config):
    logging.info('[{}] Generating Kconfig symbol del count per commit...'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_kdef_count_change_type)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])
    df['only_del'] = df['only_del'].apply(ast.literal_eval)

    result = []
    for _, row in df.iterrows():
        if row['only_del_count'] > 0:
            result.append({'sha': row['sha'], 
                           'commit.committer.date': row['commit.committer.date'],
                           'only_del_count': row['only_del_count'], 
                           'only_del': row['only_del']})
    df = pd.DataFrame(result)

    # Calculate time distance between add commits
    df['time_distance'] = 0
    for i in range(1, df.shape[0]):
        df.at[i, 'time_distance'] = (df.iloc[i]['commit.committer.date']
                                     - df.iloc[i-1]['commit.committer.date']
                                     ).total_seconds()
    df = df[['sha','commit.committer.date','only_del_count','time_distance',
             'only_del']]
    df.to_csv(project_config.file_kdef_del_count_per_commit,
              header=True, index=False)


def kdef_add_del_count_per_commit(project_config):
    logging.info('[{}] Generating Kconfig symbol add delete count per commit...'
                 .format(project_config.project_name))
    df_add = read_csv_to_df(project_config.file_kdef_add_count_per_commit)
    df_del = read_csv_to_df(project_config.file_kdef_del_count_per_commit)

    df_add['commit.committer.date'] = pd.to_datetime(df_add['commit.committer.date'])
    df_del['commit.committer.date'] = pd.to_datetime(df_del['commit.committer.date'])

    df_add['commit.committer.date'] = df_add['commit.committer.date'].dt.year
    df_del['commit.committer.date'] = df_del['commit.committer.date'].dt.year

    df_add = df_add.rename(columns={'commit.committer.date': 'year', 'only_add_count': 'add_count'})
    df_del = df_del.rename(columns={'commit.committer.date': 'year', 'only_del_count': 'del_count'})

    df_add = df_add[['sha', 'year', 'add_count']]
    df_del = df_del[['sha', 'year', 'del_count']]

    df = pd.merge(df_add, df_del, on=['sha', 'year'], how='outer')

    df['add_count'] = df['add_count'].fillna(0)
    df['del_count'] = df['del_count'].fillna(0)
    df['add_count'] = df['add_count'].astype(int)
    df['del_count'] = df['del_count'].astype(int)

    df = df.sort_values(by='year')

    df.to_csv(project_config.file_kdef_add_del_count_per_commit,
              header=True, index=False)
