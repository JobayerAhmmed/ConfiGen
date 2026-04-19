import os
import re

import config


repo_url = 'https://github.com/wbx-github/uclibc-ng.git'
repo_branch = 'master'

project_dir_name = 'uclibc-ng'
project_name = 'uClibc-ng'
project_data_dir = os.path.join(config.data_dir, project_dir_name)
project_repo_dir = os.path.join(config.temp_dir, project_dir_name)
project_xml_dir = os.path.join(config.xml_dir, project_dir_name, 'kconfig')
project_doc_dir = os.path.join(config.temp_dir, 'autoconf_doc', project_dir_name)
project_xml_doc_dir = os.path.join(config.temp_dir, 'xml_doc', project_dir_name)
project_doxygen_doc_dir = os.path.join(config.temp_dir, 'doxygen_doc', project_dir_name)
project_image_dir = os.path.join(config.image_dir, project_dir_name)
project_doxyfile = os.path.join(config.root_dir, 'Doxyfile_uclibc')
project_gen_config_file = None
project_xml_diff_dir = os.path.join(config.temp_dir, 'diff', project_dir_name, 'xml_diff')
project_html_diff_dir = os.path.join(config.temp_dir, 'diff', project_dir_name, 'html_diff')
project_doxy_auto_diff_dir = os.path.join(config.temp_dir, 'doxygen_autoconfdoc_diff', project_dir_name, 'html_diff')
project_doxy_diff_data_html_dir = os.path.join(config.xml_dir, 'doxygen_autoconfdoc_diff', project_dir_name, 'html_diff')
project_auto_diff_data_html_dir = os.path.join(config.xml_dir, 'diff', project_dir_name, 'html_diff')

file_commit_ids = os.path.join(project_data_dir, 'commit_ids.csv')
file_config_issues = os.path.join(project_data_dir, 'config_issues.csv')
file_commit_ids_doc_gen_status = os.path.join(
    project_data_dir, 'commit_ids_doc_gen_status.csv')
file_commit_ids_add_del_kdef = os.path.join(
    project_data_dir, 'commit_ids_add_del_kdef.csv')
file_commit_ids_random = os.path.join(
    project_data_dir, 'commit_ids_random.csv')
file_commit_ids_kdef_test_cases = os.path.join(
    project_data_dir, 'commit_ids_kdef_test_cases.csv')
file_commit_ids_random_kdef_no_test = os.path.join(
    project_data_dir, 'commit_ids_random_kdef_no_test.csv')
file_commit_ids_random_kdef = os.path.join(
    project_data_dir, 'commit_ids_random_kdef.csv')
file_commit_ids_random_non_kdef = os.path.join(
    project_data_dir, 'commit_ids_random_non_kdef.csv')
file_commit_ids_versions = os.path.join(
    project_data_dir, 'commit_ids_versions.csv')
file_commit_ids_versions_doxygen_time = os.path.join(
    project_data_dir, 'commit_ids_versions_doxygen_time.csv')
file_commit_ids_versions_configen_time = os.path.join(
    project_data_dir, 'commit_ids_versions_configen_time.csv')

file_commit_data = os.path.join(project_data_dir, 'commit_data.csv')

file_kdef_commits = os.path.join(project_data_dir, 'kdef_commits.csv')
file_code_commits = os.path.join(project_data_dir, 'code_commits.csv')
file_kdef_code_commits = os.path.join(
    project_data_dir, 'kdef_code_commits.csv')
file_other_commits = os.path.join(project_data_dir, 'other_commits.csv')
file_no_change_commits = os.path.join(
    project_data_dir, 'no_change_commits.csv')

file_kdef = os.path.join(project_data_dir, 'kdef.csv')
file_kdef_count_change_type = os.path.join(
    project_data_dir, 'kdef_count_change_type.csv')

fig_commit_count = os.path.join(project_image_dir, 'commit_count.svg')
file_commit_count = os.path.join(project_data_dir, 'commit_count.csv')
fig_commit_count_per_year = os.path.join(
    project_image_dir, 'commit_count_per_year.svg')
file_commit_count_per_year = os.path.join(
    project_data_dir, 'commit_count_per_year.csv')
fig_commit_count_per_year_commit_type = os.path.join(
    project_image_dir, 'commit_count_per_year_commit_type.svg')
file_commit_count_per_year_commit_type = os.path.join(
    project_data_dir, 'commit_count_per_year_commit_type.csv')
fig_commit_count_per_month_commit_type = os.path.join(
    project_image_dir, 'commit_count_per_month_commit_type.svg')
file_commit_count_per_month_commit_type = os.path.join(
    project_data_dir, 'commit_count_per_month_commit_type.csv')
fig_commit_count_per_week_commit_type = os.path.join(
    project_image_dir, 'commit_count_per_week_commit_type.svg')
file_commit_count_per_week_commit_type = os.path.join(
    project_data_dir, 'commit_count_per_week_commit_type.csv')
fig_commit_count_per_year_change_type = os.path.join(
    project_image_dir, 'commit_count_per_year_change_type.svg')
file_commit_count_per_year_change_type = os.path.join(
    project_data_dir, 'commit_count_per_year_change_type.csv')

file_doxy_diff_changes_summary = os.path.join(project_data_dir,
                                              'diff_changes_summary.csv')

fig_file_count = os.path.join(project_image_dir, 'file_count.svg')
file_file_count = os.path.join(project_data_dir, 'file_count.csv')
fig_file_count_per_year = os.path.join(
    project_image_dir, 'file_count_per_year.svg')
file_file_count_per_year = os.path.join(
    project_data_dir, 'file_count_per_year.csv')
fig_file_count_per_commit = os.path.join(
    project_image_dir, 'file_count_per_commit.svg')
file_file_count_per_commit_kconf = os.path.join(
    project_data_dir, 'file_count_per_commit_kconf.csv')
file_file_count_per_commit_nonkconf = os.path.join(
    project_data_dir, 'file_count_per_commit_nonkconf.csv')

fig_kdef_count = os.path.join(project_image_dir, 'kdef_count.svg')
fig_kdef_count_pie_chart = os.path.join(
    project_image_dir, 'kdef_count_pie_chart.svg')
file_kdef_count = os.path.join(project_data_dir, 'kdef_count.csv')
fig_kdef_count_per_year_change_type = os.path.join(
    project_image_dir, 'kdef_count_per_year_change_type.svg')
file_kdef_count_per_year_change_type = os.path.join(
    project_data_dir, 'kdef_count_per_year_change_type.csv')
file_kdef_add_count_per_commit = os.path.join(
    project_data_dir, 'kdef_add_count_per_commit.csv')
fig_kdef_add_count_per_commit = os.path.join(
    project_image_dir, 'kdef_add_count_per_commit.pdf')
file_kdef_del_count_per_commit = os.path.join(
    project_data_dir, 'kdef_del_count_per_commit.csv')
file_kdef_add_del_count_per_commit = os.path.join(
    project_data_dir, 'kdef_add_del_count_per_commit.csv')
fig_kdef_add_del_count_per_commit = os.path.join(
    project_image_dir, 'kdef_add_del_count_per_commit.pdf')

file_kdef_add_count_per_month = os.path.join(
    project_data_dir, 'kdef_add_count_per_month.csv')
fig_kdef_add_count_per_month = os.path.join(
    project_image_dir, 'kdef_add_count_per_month.pdf')

file_kdef_add_count_per_year = os.path.join(
    project_data_dir, 'kdef_add_count_per_year.csv')
fig_kdef_add_count_per_year = os.path.join(
    project_image_dir, 'kdef_add_count_per_year.pdf')
    
file_kdef_xml_count = os.path.join(
    project_data_dir, 'kdef_xml_count.csv')
fig_kdef_xml_count_per_commit = os.path.join(
    project_image_dir, 'kdef_xml_count_per_commit.svg')
file_kdef_xml_count_per_commit = os.path.join(
    project_data_dir, 'kdef_xml_count_per_commit.csv')
fig_kdef_xml_usage_count_per_add_kdef = os.path.join(
    project_image_dir, 'kdef_xml_usage_count_per_add_kdef.svg')
fig_kdef_xml_usage_count_per_del_kdef = os.path.join(
    project_image_dir, 'kdef_xml_usage_count_per_del_kdef.svg')
file_kdef_xml_usage_count_per_add_del_kdef = os.path.join(
    project_data_dir, 'kdef_xml_usage_count_per_add_del_kdef.csv')

file_auto_diff_summary = os.path.join(project_data_dir, 'auto_diff_summary.csv')

# First commit, 2000-05-14
start_commit_id = '64bc6412188b141c010ac3b8e813b837dd991e80'
# Last commit of 2023, 2023-12-22
end_commit_id = 'de8c46aee404020fb78a6a283b5be6fbee4f3931'
# First commit of 2004, 2004-01-02
config_prefix_start_commit_id = '9f04c85b35a0efa6009e610d45dfb3f5d2dbfa22'

kdef_start = None
kdef_add = None
kdef_del = None
kdef_body = None
kdef_edit_plus = None
kdef_edit_minus = None

kdef_in_src_start = re.compile(
    '^(?:[ \t]*config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')
kdef_in_src_add = re.compile(
    '^(?:\+[ \t]*config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')
kdef_in_src_del = re.compile(
    '^(?:-[ \t]*config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')

# Lines that start with either two or more consecutive spaces,
# or, one or more tab character;
# or contain only whitespace characters (including empty lines)
kdef_in_src_body = re.compile('^(?: {2,}|\t+).*|\s*$')

kdef_in_src_edit_plus = re.compile('^\+(?: {2,}|\t+).*$')
kdef_in_src_edit_minus = re.compile('^-(?: {2,}|\t+).*$')

source_file_pattern = ('*.c', '*.h')
config_file_pattern = ('Config.*',)
macro_prefixes = ('__',)
macro_suffixes = ('__',)
