"""Run AutoConfDoc to generate documentation for a commit.

Code to create a csv file containing commit ids with
documentation generation status, and to move the Kconfig
XML files to project specific XML directory.
"""

import subprocess
import logging
import shutil
import os
import ast
import time

import pandas as pd
import progressbar

from utils import read_csv_to_df



def run_autoconf_doc(project_config):
    gen_commit_ids_doc_gen_status_file(project_config)
    generate_autoconf_xmls(project_config)
    
    # generate_doc(project_config, '6fc08ddc732c8c0a56391d30d4e86aa46bda5495', 'yes')
    pass


def generate_autoconf_doc_for_versions(project_config):
    version_df = read_csv_to_df(project_config.file_commit_ids_versions)
    time_data = []
    for _, row in version_df.iterrows():
        start_time = time.time()
        return_value = generate_doc_for_version(project_config, row, 'yes')
        end_time = time.time()
        time_taken = end_time - start_time
        if return_value != -1:
            copy_xml(project_config, row['sha'])
        else:
            time_taken = -1
        time_data.append({'tag': row['tag'], 'year': row['year'], 'time': time_taken})
    time_data.reverse()
    time_df = pd.DataFrame(time_data)
    time_df.to_csv(project_config.file_commit_ids_versions_configen_time, header=True, index=False)


def gen_commit_ids_doc_gen_status_file(project_config):
    """Reads commit_ids.csv and creates commit_ids_doc_gen_status.csv.

    Includes column:
    - doc_gen_status: default value 'fail', denotes ConfiGen runs successfully
    - config_entry_file: entry file for kextract to read configs from
    - gen_config_cmd: command to run the script that generates Config.in files

    Parameters
    ----------
    project_config
        Project specific config options.
    """
    logging.info('[{}] Generating file commit_ids_doc_gen_status.csv'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_commit_ids)

    start_row = (df[df['sha'] == project_config.config_prefix_start_commit_id]
                 .index[0])
    df = df[start_row:]
    df = df.reset_index(drop=True)

    df['doc_gen_status'] = 'fail'
    df['gen_config_cmd'] = ''
    df['config_entry_file'] = 'Config.in'
    df['config_issues'] = [[] for _ in range(len(df))]

    # 
    # BusyBox
    #   gen_config_cmd: ./scripts/gen_build_files.sh . .
    #       from commit: 7fb68f199f037cb69363c8df5c934a27adc699f7
    #   config_entry_file: Config.in
    # uClibc-ng
    #   gen_config_cmd: empty, all configs are Config.in files
    #   config_entry_file: extra/Configs/Config.in
    #       6625518cd6894338937a74ca6b9187b7b8167b03 
    #       ~ 39142c932fccc38c3323a1d1ae9eb743d1bef01c: extra/Configs/Config.alpha
    # Toybox
    #   gen_config_cmd: ./scripts/genconfig.sh
    #       from commit: 2896480c4918f2accccb8301bec457a7bff7377e,2008-01-19
    #       which is before the first commit:
    #       9317c06e2d2081feb37ab36e626707f3a1205576,2012-03-07
    #   config_entry_file: Config.in
    if project_config.project_dir_name == 'busybox':
        config_cmd_index = df.index[
            df['sha'] == '7fb68f199f037cb69363c8df5c934a27adc699f7'].tolist()
        if len(config_cmd_index) > 0:
            df.loc[config_cmd_index[0]:,
                   'gen_config_cmd'] = 'scripts/gen_build_files.sh . .'
    elif project_config.project_dir_name == 'uclibc-ng':
        df['config_entry_file'] = 'extra/Configs/Config.in'
        alpha_start = df.index[
            df['sha'] == '6625518cd6894338937a74ca6b9187b7b8167b03'].tolist()
        alpha_end = df.index[
            df['sha'] == '39142c932fccc38c3323a1d1ae9eb743d1bef01c'].tolist()
        if len(alpha_start) > 0 and len(alpha_end) > 0:
            df.loc[alpha_start[0]: alpha_end[0],
                   'config_entry_file'] = 'extra/Configs/Config.alpha'
    elif project_config.project_dir_name == 'toybox':
        df['gen_config_cmd'] = 'scripts/genconfig.sh'

    # 
    # Update config_issues field from config_issues.csv file
    config_issues_df = read_csv_to_df(project_config.file_config_issues)
    config_issues_df.set_index('sha', inplace=True)
    df.set_index('sha', inplace=True)
    df.update(config_issues_df)
    df.reset_index(inplace=True)

    # 
    # Update doc_gen_status field from old file
    # old_df = read_csv_to_df(project_config.file_commit_ids_doc_gen_status)
    # for index, row in df.iterrows():
    #     i = old_df[old_df['sha'] == row['sha']].index.tolist()
    #     if len(i) > 0:
    #         df.at[index, 'doc_gen_status'] = old_df.iloc[i[0]]['doc_gen_status']
    #     else:
    #         logging.error('[{}] Cannot find commit {} in old doc_gen_status file'
    #                       .format(project_config.project_name, row['sha'][:7]))

    df.to_csv(project_config.file_commit_ids_doc_gen_status, header=True,
              index=False)


def generate_autoconf_xmls(project_config):
    """Reads commit_ids_doc_gen_status.csv and run ConfiGen
    to generate kconfig_defs.xml and kconfig_usage.xml files.

    Parameters
    ----------
    project_config
        Project specific config options.
    """
    logging.info('[{}] Generating Kconfig XMLs by ConfiGen...'
                 .format(project_config.project_name))
    df = read_csv_to_df(project_config.file_commit_ids_doc_gen_status)
    bar = progressbar.ProgressBar(max_value=len(df), redirect_stdout=True).start()
    
    for index, row in df.iterrows():
        # if row['doc_gen_status'] == 'success':
        #     continue
        r = generate_doc(project_config, row['sha'], 'no')
        if r == -1:
            continue
        copy_xml(project_config, row['sha'], 'no')
        df.at[index, 'doc_gen_status'] = 'success'
        df.to_csv(project_config.file_commit_ids_doc_gen_status, header=True,
                  index=False)
        bar.update(index + 1)
    bar.finish()


def generate_doc(project_config, commit_id, is_generate_doc='yes'):
    """Run ConfiGen to generate documentation.

    The documentation is placed inside the directory created
    using the commit id. Commit id directory is created inside
    the project specific project_doc_dir.
    
    Parameters
    ----------
    project_config
        Project specific config options.
    commit_id: str
        Commit id for which the doc will be generated.
    is_generate_doc: str
        Whether to generate doc or only Kconfig XML files without doc.
    """
    logging.info('[{}] Generating documentation by ConfiGen for {}'
                 .format(project_config.project_name, commit_id[:7]))

    # Make the repository ready.
    logging.info('Setting up project repository...')
    if os.path.isdir(project_config.project_repo_dir):
        os.chdir(project_config.project_repo_dir)
    else:
        logging.error('[{}] Project repository does not exist! Clone the project.'
                      .format(project_config.project_name))
        return -1
    r = subprocess.run(['git', 'clean', '-fxdq'])
    if r.returncode != 0:
        logging.error('[{}] Failed to git clean for {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    r = subprocess.run(['git', 'reset', '--hard', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to git reset for {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    r = subprocess.run(['git', 'checkout', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to checkout to {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    
    doc_gen_df = read_csv_to_df(project_config.file_commit_ids_doc_gen_status)
    commit_row_index = doc_gen_df.index[doc_gen_df['sha'] == commit_id].tolist()
    if len(commit_row_index) < 1:
        logging.error('[{}] Could not find commit {} in commit_ids_doc_gen_status.csv'
                      .format(project_config.project_name, commit_id[:7]))    
        return -1
    gen_config_cmd = doc_gen_df.loc[commit_row_index[0], 'gen_config_cmd']
    config_entry_file = doc_gen_df.loc[commit_row_index[0], 'config_entry_file']
    config_issues = doc_gen_df.loc[commit_row_index[0], 'config_issues']
    config_issues = ast.literal_eval(config_issues)
    
    # Generate Config.in files
    if not pd.isna(gen_config_cmd) and gen_config_cmd:
        logging.info('Generating Kconfig files...')
        cmd = ['chmod', '744', gen_config_cmd.split()[0]]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            logging.error('[{}] Failed to set execute permission to gen_config file for {}'
                          .format(project_config.project_name, commit_id[:7]))
            return -1
        cmd = gen_config_cmd.split()
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            logging.error('[{}] Failed to generate Kconfig files for {}'
                          .format(project_config.project_name, commit_id[:7]))
            return -1

    # Fix config issues
    for item in config_issues:
        filepath = os.path.join(project_config.project_repo_dir, item['filename'])
        with open(filepath, 'rb') as f:
            file_data = f.read()
        file_str = file_data.decode(encoding='utf-8', errors='ignore')
        lines = file_str.split('\n')
        for i in range(len(lines)):
            line = lines[i].strip()
            if line == item['line_str']:
                new_line = lines[i].replace(item['line_str'],
                                            item['replace_with'], 1)
                lines[i] = new_line
                break
        file_str = '\n'.join(lines)
        with open(filepath, 'w') as f:
            f.write(file_str)
    
    # Update Doxyfile
    with open(project_config.project_doxyfile, 'r') as f:
        lines = f.readlines()
    output_dir = os.path.join(project_config.project_doc_dir, commit_id)
    if is_generate_doc == 'no':
        output_dir = os.path.join(project_config.project_xml_doc_dir, commit_id)
    for i in range(len(lines)):
        if lines[i].strip().startswith('OUTPUT_DIRECTORY '):
            lines[i] = 'OUTPUT_DIRECTORY = ' + output_dir + '\n'
            break
    if is_generate_doc == 'no':
        for i in range(len(lines)):
            if lines[i].strip().startswith('GENERATE_DOC '):
                lines[i] = 'GENERATE_DOC = NO\n'
                break
    for i in range(len(lines)):
        if lines[i].strip().startswith('KCONFIG_ENTRY_FILE '):
            lines[i] = 'KCONFIG_ENTRY_FILE = ' + config_entry_file + '\n'
            break
    with open(os.path.join(project_config.project_repo_dir, 'Doxyfile'), 'w') as f:
        f.writelines(lines)
    
    logging.info('Running ConfiGen...')
    r = subprocess.run(['doxygen'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        logging.error('[{}] Failed to run ConfiGen for commit {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    return 0


def copy_xml(project_config, commit_id, is_generate_doc='yes'):
    src_def_xml = os.path.join(project_config.project_doc_dir,
                               commit_id, 'html', 'kconfig',
                               'kconfig_defs.xml')
    src_usage_xml = os.path.join(project_config.project_doc_dir,
                                 commit_id, 'html', 'kconfig',
                                 'kconfig_usage.xml')
    dst_def_xml = os.path.join(project_config.project_xml_dir,
                               commit_id + '_defs.xml')
    dst_usage_xml = os.path.join(project_config.project_xml_dir,
                                 commit_id + '_usage.xml')
    if is_generate_doc == 'no':
        src_def_xml = os.path.join(project_config.project_xml_doc_dir,
                                   commit_id, 'html', 'kconfig',
                                   'kconfig_defs.xml')
        src_usage_xml = os.path.join(project_config.project_xml_doc_dir,
                                     commit_id, 'html', 'kconfig',
                                     'kconfig_usage.xml')
    if os.path.isfile(src_def_xml) and os.path.isfile(src_usage_xml):
        shutil.copy(src_def_xml, dst_def_xml)
        shutil.copy(src_usage_xml, dst_usage_xml)
    else:
        logging.error('[{}] Could not find XML files for {}'
                      .format(project_config.project_name, commit_id[:7]))


def generate_doc_for_version(project_config, version_row, is_generate_doc='yes'):
    """Run ConfiGen to generate documentation.

    The documentation is placed inside the directory created
    using the commit id. Commit id directory is created inside
    the project specific project_doc_dir.
    
    Parameters
    ----------
    project_config
        Project specific config options.
    commit_id: str
        Commit id for which the doc will be generated.
    is_generate_doc: str
        Whether to generate doc or only Kconfig XML files without doc.
    """
    commit_id = version_row['sha']
    gen_config_cmd = version_row['gen_config_cmd']
    config_entry_file = version_row['config_entry_file']
    config_issues = version_row['config_issues']
    config_issues = ast.literal_eval(config_issues)

    logging.info('[{}] Generating documentation by ConfiGen for {}'
                 .format(project_config.project_name, commit_id[:7]))

    # Make the repository ready.
    logging.info('Setting up project repository...')
    if os.path.isdir(project_config.project_repo_dir):
        os.chdir(project_config.project_repo_dir)
    else:
        logging.error('[{}] Project repository does not exist! Clone the project.'
                      .format(project_config.project_name))
        return -1
    r = subprocess.run(['git', 'clean', '-fxdq'])
    if r.returncode != 0:
        logging.error('[{}] Failed to git clean for {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    r = subprocess.run(['git', 'reset', '--hard', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to git reset for {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    r = subprocess.run(['git', 'checkout', commit_id])
    if r.returncode != 0:
        logging.error('[{}] Failed to checkout to {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    
    
    # Generate Config.in files
    if not pd.isna(gen_config_cmd) and gen_config_cmd:
        logging.info('Generating Kconfig files...')
        cmd = ['chmod', '744', gen_config_cmd.split()[0]]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            logging.error('[{}] Failed to set execute permission to gen_config file for {}'
                          .format(project_config.project_name, commit_id[:7]))
            return -1
        cmd = gen_config_cmd.split()
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            logging.error('[{}] Failed to generate Kconfig files for {}'
                          .format(project_config.project_name, commit_id[:7]))
            return -1

    # Fix config issues
    for item in config_issues:
        filepath = os.path.join(project_config.project_repo_dir, item['filename'])
        with open(filepath, 'rb') as f:
            file_data = f.read()
        file_str = file_data.decode(encoding='utf-8', errors='ignore')
        lines = file_str.split('\n')
        for i in range(len(lines)):
            line = lines[i].strip()
            if line == item['line_str']:
                new_line = lines[i].replace(item['line_str'],
                                            item['replace_with'], 1)
                lines[i] = new_line
                break
        file_str = '\n'.join(lines)
        with open(filepath, 'w') as f:
            f.write(file_str)
    
    # Update Doxyfile
    with open(project_config.project_doxyfile, 'r') as f:
        lines = f.readlines()
    output_dir = os.path.join(project_config.project_doc_dir, commit_id)
    if is_generate_doc == 'no':
        output_dir = os.path.join(project_config.project_xml_doc_dir, commit_id)
    for i in range(len(lines)):
        if lines[i].strip().startswith('OUTPUT_DIRECTORY '):
            lines[i] = 'OUTPUT_DIRECTORY = ' + output_dir + '\n'
            break
    if is_generate_doc == 'no':
        for i in range(len(lines)):
            if lines[i].strip().startswith('GENERATE_DOC '):
                lines[i] = 'GENERATE_DOC = NO\n'
                break
    for i in range(len(lines)):
        if lines[i].strip().startswith('KCONFIG_ENTRY_FILE '):
            lines[i] = 'KCONFIG_ENTRY_FILE = ' + config_entry_file + '\n'
            break
    with open(os.path.join(project_config.project_repo_dir, 'Doxyfile'), 'w') as f:
        f.writelines(lines)
    
    logging.info('Running ConfiGen...')
    r = subprocess.run(['doxygen'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        logging.error('[{}] Failed to run ConfiGen for commit {}'
                      .format(project_config.project_name, commit_id[:7]))
        return -1
    return 0
