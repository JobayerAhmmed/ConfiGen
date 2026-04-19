"""Generate HTML documentation by Doxygen."""

import logging
import os
import subprocess
import time

import pandas as pd

from config import root_dir
from utils import read_csv_to_df



def generate_doxygen_doc_for_versions(project_config):
    df = read_csv_to_df(project_config.file_commit_ids_versions)
    time_data = []
    for _, row in df.iterrows():
        start_time = time.time()
        ret_value = generate_doc(project_config, row['sha'])
        end_time = time.time()
        time_taken = end_time - start_time
        if ret_value == -1:
            time_taken = -1
        time_data.append({'tag': row['tag'], 'year': row['year'], 'time': time_taken})
    time_data.reverse()
    time_df = pd.DataFrame(time_data)
    time_df.to_csv(project_config.file_commit_ids_versions_doxygen_time, header=True, index=False)


def generate_doc(project_config, commit_id: str):
    """Run Doxygen to generate documentation.

    The documentation is placed inside the directory created
    using the commit id. Commit id directory is created inside
    the project specific project_doc_dir.
    
    Parameters
    ----------
    project_config
        Project specific config options.
    commit_id : str
        Commit id for which the doc will be generated.
    """
    logging.info('[{}] Generating documentation by Doxygen for {}'
                 .format(project_config.project_name, commit_id[:7]))

    # Make the repository ready.
    logging.info('Setting up project repository...')
    if os.path.isdir(project_config.project_repo_dir):
        os.chdir(project_config.project_repo_dir)
    else:
        logging.error('Project repository does not exist! Clone the project.')
        return -1
    r = subprocess.run(['git', 'clean', '-fxdq'])
    if r.returncode != 0:
        logging.error('Failed to git clean for ' + commit_id[:7])
        return -1
    r = subprocess.run(['git', 'reset', '--hard', commit_id])
    if r.returncode != 0:
        logging.error('Failed to git reset for ' + commit_id[:7])
        return -1
    r = subprocess.run(['git', 'checkout', commit_id])
    if r.returncode != 0:
        logging.error('Failed to checkout to ' + commit_id[:7])
        return -1
    
    update_doxyfile(project_config, commit_id)
    
    logging.info('Running Doxygen...')
    doxygen_bin = os.path.join(os.path.dirname(root_dir), 'doxygen', 'build',
                               'bin', 'doxygen')
    r = subprocess.run([doxygen_bin], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        logging.error('Failed to run Doxygen for ' + commit_id[:7])
        return -1
    return 0


def update_doxyfile(project_config, commit_id):
    logging.info('Updating Doxyfile...')
    with open(project_config.project_doxyfile, 'r') as f:
        lines = f.readlines()

    # Update OUTPUT_DIRECTORY
    output_dir = os.path.join(project_config.project_doxygen_doc_dir, commit_id)
    for i in range(len(lines)):
        if lines[i].strip().startswith('OUTPUT_DIRECTORY '):
            lines[i] = 'OUTPUT_DIRECTORY = ' + output_dir + '\n'
            break

    # Comment out tags added for AutoConfDoc
    # KCONFIG_ENTRY_FILE
    # KCONFIG_MACRO_PREFIX
    # KCONFIG_MACRO_SUFFIX
    # GENERATE_DOC
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('KCONFIG_') or line.startswith('GENERATE_DOC '):
            lines[i] = '#' + lines[i] + '\n'
    
    with open(os.path.join(project_config.project_repo_dir, 'Doxyfile'),
              'w') as f:
        f.writelines(lines)
