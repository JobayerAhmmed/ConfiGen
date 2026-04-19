import os
import re

root_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
xml_dir = os.path.join(os.path.dirname(root_dir), 'data')
image_dir = os.path.join(root_dir, 'doc', 'images')
data_dir = os.path.join(root_dir, 'commit_parser', 'data')
temp_dir = os.path.join(data_dir, 'temp')

fig_commit_count_per_year = os.path.join(image_dir, 'commit_count_per_year.pdf')
fig_q1_busybox_line_graph = os.path.join(image_dir, 'q1_busybox_line_graph.pdf')
fig_q1_uclibc_line_graph = os.path.join(image_dir, 'q1_uclibc_line_graph.pdf')
fig_q1_toybox_line_graph = os.path.join(image_dir, 'q1_toybox_line_graph.pdf')

file_file_count = os.path.join(data_dir, 'file_count.csv')
file_file_count_per_year = os.path.join(data_dir, 'file_count_per_year.csv')
file_commit_file_kdef_count_per_year = os.path.join(data_dir, 'commit_file_kdef_count_per_year.csv')
file_kdef_xml_count_table1 = os.path.join(data_dir, 'kdef_xml_count_table1.csv')
file_kdef_xml_count_table2 = os.path.join(data_dir, 'kdef_xml_count_table2.csv')

log_file = os.path.join(data_dir, 'commit_parser.log')
