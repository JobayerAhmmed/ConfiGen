import os
import re

import config


repo_url = 'https://git.busybox.net/busybox/'
repo_branch = 'master'

project_dir_name = 'busybox'
project_name = 'BusyBox'
project_data_dir = os.path.join(config.data_dir, project_dir_name)
project_repo_dir = os.path.join(config.temp_dir, project_dir_name)
project_xml_dir = os.path.join(config.xml_dir, project_dir_name, 'kconfig')
project_doc_dir = os.path.join(config.temp_dir, 'autoconf_doc', project_dir_name)
project_xml_doc_dir = os.path.join(config.temp_dir, 'xml_doc', project_dir_name)
project_doxygen_doc_dir = os.path.join(config.temp_dir, 'doxygen_doc', project_dir_name)
project_image_dir = os.path.join(config.image_dir, project_dir_name)
project_doxyfile = os.path.join(config.root_dir, 'Doxyfile_bbox')
project_gen_config_file = os.path.join(config.root_dir, 'gen_config_files_bbox.sh')
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
file_test_case_symbols = os.path.join(
    project_data_dir, 'test_case_symbols.csv')
file_test_case_symbols_commits = os.path.join(
    project_data_dir, 'test_case_symbols_commits.csv')

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

# First commit, 1999-10-05
start_commit_id = 'cc8ed39b240180b58810784f844e253263594ac3'
# Last commit of 2023, 2023-12-31
end_commit_id = '01e80ff9ebaf42f2fb9b4ddddc75d37bc9a403aa'
# 2006-10-05
config_prefix_start_commit_id = '7d219aab70e6951ab82c27c202cac05016696723'
# 2002-12-05
config_start_commit_id = 'c9f20d9fb93c6c316518483fd103f3afab5cf1af'

kdef_start = re.compile(
    '^(?:[ \t]*//config:config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')
kdef_add = re.compile(
    '^(?:\+[ \t]*//config:config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')
kdef_del = re.compile(
    '^(?:-[ \t]*//config:config[ \t]+)([A-Z][A-Za-z0-9_]*)[ \t]*(?:#.*)?$')

# Lines that start with //config: but not with //config:config
kdef_body = re.compile('^[ \t]*//config:(?!config)(?:(?: {2,}|\t+).*|\s*)$')
kdef_edit_plus = re.compile('^\+[ \t]*//config:(?!config)(?:(?: {2,}|\t+).*|\s*)$')
kdef_edit_minus = re.compile('^-[ \t]*//config:(?!config)(?:(?: {2,}|\t+).*|\s*)$')

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
config_file_pattern = ('Config.src', 'Config.in')
macro_prefixes = ('ENABLE_', 'CONFIG_')
macro_suffixes = ()
