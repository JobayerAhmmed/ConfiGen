import logging
import os
import subprocess

import config
import config_bbox
import config_uclibc
import config_toybox
from utils import *
from commit_data import run_commit_data
from commit_count import run_commit_count
from commit_count import commit_count_per_year
from kdef import run_kdef
from doxygen_doc import generate_doxygen_doc_for_versions
from autoconf_doc import generate_autoconf_doc_for_versions
from autoconf_doc import run_autoconf_doc
from doxygen_doc_diff import run_doxygen_doc_diff
from xml_diff import run_xml_diff
from version_commit import generate_version_commit_ids


def create_dirs():
    """Create required directories for commit analysis."""
    create_dir(config_bbox.project_data_dir)
    create_dir(config_uclibc.project_data_dir)
    create_dir(config_toybox.project_data_dir)

    create_dir(config_bbox.project_doc_dir)
    create_dir(config_uclibc.project_doc_dir)
    create_dir(config_toybox.project_doc_dir)

    create_dir(config_bbox.project_xml_doc_dir)
    create_dir(config_uclibc.project_xml_doc_dir)
    create_dir(config_toybox.project_xml_doc_dir)

    create_dir(config_bbox.project_doxygen_doc_dir)
    create_dir(config_uclibc.project_doxygen_doc_dir)
    create_dir(config_toybox.project_doxygen_doc_dir)

    create_dir(config_bbox.project_image_dir)
    create_dir(config_uclibc.project_image_dir)
    create_dir(config_toybox.project_image_dir)

    create_dir(config_bbox.project_xml_dir)
    create_dir(config_uclibc.project_xml_dir)
    create_dir(config_toybox.project_xml_dir)

    create_dir(config_bbox.project_xml_diff_dir)
    create_dir(config_uclibc.project_xml_diff_dir)
    create_dir(config_toybox.project_xml_diff_dir)

    create_dir(config_bbox.project_html_diff_dir)
    create_dir(config_uclibc.project_html_diff_dir)
    create_dir(config_toybox.project_html_diff_dir)

    create_dir(config_bbox.project_doxy_auto_diff_dir)
    create_dir(config_uclibc.project_doxy_auto_diff_dir)
    create_dir(config_toybox.project_doxy_auto_diff_dir)

    create_dir(config_bbox.project_doxy_diff_data_html_dir)
    create_dir(config_uclibc.project_doxy_diff_data_html_dir)
    create_dir(config_toybox.project_doxy_diff_data_html_dir)

    create_dir(config_bbox.project_auto_diff_data_html_dir)
    create_dir(config_uclibc.project_auto_diff_data_html_dir)
    create_dir(config_toybox.project_auto_diff_data_html_dir)


def clone_project_repos():
    clone_repo(config_bbox.repo_url, config_bbox.project_repo_dir, config.temp_dir)
    clone_repo(config_uclibc.repo_url, config_uclibc.project_repo_dir, config.temp_dir)
    clone_repo(config_toybox.repo_url, config_toybox.project_repo_dir, config.temp_dir)


if __name__ == "__main__":
    create_dirs()

    formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.NOTSET)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename=config.log_file, mode='a',
                                       encoding='utf-8')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # clone_project_repos()


    # 
    # Pre-Study
    # 
    # run_commit_data(config_bbox)
    # run_commit_data(config_uclibc)
    # run_commit_data(config_toybox)

    # commit_count_per_year(config_bbox)
    # commit_count_per_year(config_uclibc)
    # commit_count_per_year(config_toybox)

    # run_commit_count(config_bbox)
    # run_commit_count(config_uclibc)
    # run_commit_count(config_toybox)

    # run_kdef(config_bbox)
    # run_kdef(config_uclibc)
    # run_kdef(config_toybox)

    # file_count_per_year(config_bbox)
    # file_count_per_year(config_uclibc)
    # file_count_per_year(config_toybox)
    # file_count_per_year_all(config, config_bbox, config_uclibc, config_toybox)


    # 
    # Q1
    #
    # generate_version_commit_ids(config_bbox)
    # generate_version_commit_ids(config_uclibc)
    # generate_version_commit_ids(config_toybox)

    # generate_doxygen_doc_for_versions(config_bbox)
    # generate_doxygen_doc_for_versions(config_uclibc)
    # generate_doxygen_doc_for_versions(config_toybox)

    # generate_autoconf_doc_for_versions(config_bbox)
    # generate_autoconf_doc_for_versions(config_uclibc)
    # generate_autoconf_doc_for_versions(config_toybox)

    # run_doxygen_doc_diff(config_bbox)
    # run_doxygen_doc_diff(config_uclibc)
    # run_doxygen_doc_diff(config_toybox)


    # 
    # Q2
    # 
    # File: file_commit_ids_versions_doxygen_time
    # File: file_commit_ids_versions_configen_time


    # 
    # Q3
    #
    # run_autoconf_doc(config_bbox)
    # run_autoconf_doc(config_uclibc)
    # run_autoconf_doc(config_toybox)

    # run_kdef_xml_count(config_bbox)
    # run_kdef_xml_count(config_uclibc)
    # run_kdef_xml_count(config_toybox)

    # kdef_xml_count_tables(config, config_bbox, config_uclibc, config_toybox)
    
    # run_random_commits(config_bbox)
    # run_random_commits(config_uclibc)
    # run_random_commits(config_toybox)

    # run_xml_diff(config_bbox)
    # run_xml_diff(config_uclibc)
    # run_xml_diff(config_toybox)

    # run_autoconf_doc_diff(config_bbox)
    # run_autoconf_doc_diff(config_uclibc)
    # run_autoconf_doc_diff(config_toybox)




    # file_count_by_change_type(config_bbox)
    # file_count_by_change_type(config_uclibc)
    # file_count_by_change_type(config_toybox)
    # file_count_by_change_type_all(config, config_bbox, config_uclibc, config_toybox)
    # commit_file_kdef_add_per_year_all(config, config_bbox, config_uclibc, config_toybox)
    
    # run_diff_analysis(config_bbox)

    # run_kdef_test_cases(config_bbox)
    # run_kdef_test_cases(config_toybox)

    # generate_doxygen_doc_for_versions(config_bbox)
    # run_autoconf_doc(config_bbox)
    # run_xml_diff(config_bbox)
    # run_autoconf_doc_diff(config_bbox)

    pass