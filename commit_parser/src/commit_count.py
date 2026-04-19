import pandas as pd

from utils import *


def run_commit_count(project_config):
    commit_count_per_year(project_config)
    commit_count_by_change_type(project_config)
    commit_count_per_year_change_type(project_config)
    commit_count_per_year_kdef_nonkdef(project_config)


def commit_count_per_year(project_config):
    df = read_csv_to_df(project_config.file_commit_ids)
    df['commit.committer.date'] = pd.to_datetime(df['commit.committer.date'])

    grouped_df = df.groupby([df['commit.committer.date'].dt.year])[
        'sha'].count()
    new_df = grouped_df.reset_index(name='count')
    new_df = new_df.rename(columns={'commit.committer.date': 'year'})
    new_df.to_csv(project_config.file_commit_count_per_year,
                  header=True, index=False)
    return grouped_df


def commit_count_by_change_type(project_config):
    kconf_def_commits = read_csv_to_df(project_config.file_kdef_commits)
    code_commits = read_csv_to_df(project_config.file_code_commits)
    kconf_code_commits = read_csv_to_df(project_config.file_kdef_code_commits)
    other_commits = read_csv_to_df(project_config.file_other_commits)
    no_change_commits = read_csv_to_df(project_config.file_no_change_commits)

    total_commit_count = (kconf_def_commits.shape[0]
                          + code_commits.shape[0]
                          + kconf_code_commits.shape[0]
                          + other_commits.shape[0]
                          + no_change_commits.shape[0])
    data = {
        'kconf_def_commit_count': kconf_def_commits.shape[0],
        'code_commit_count': code_commits.shape[0],
        'kconf_code_commit_count': kconf_code_commits.shape[0],
        'other_commit_count': other_commits.shape[0],
        'no_change_commit_count': no_change_commits.shape[0],
        'total': total_commit_count
    }
    df = pd.DataFrame.from_dict(data, orient='index', columns=[
                                'count']).rename_axis('commit_type')
    df.to_csv(project_config.file_commit_count)
    return data


def commit_count_by_change_type_per_month(project_config):
    kconf_def_commits = read_csv_to_df(project_config.file_kdef_commits)
    code_commits = read_csv_to_df(project_config.file_code_commits)
    kconf_code_commits = read_csv_to_df(project_config.file_kdef_code_commits)
    other_commits = read_csv_to_df(project_config.file_other_commits)
    no_change_commits = read_csv_to_df(project_config.file_no_change_commits)

    kconf_def_commits['commit.committer.date'] = pd.to_datetime(
        kconf_def_commits['commit.committer.date'])
    code_commits['commit.committer.date'] = pd.to_datetime(
        code_commits['commit.committer.date'])
    kconf_code_commits['commit.committer.date'] = pd.to_datetime(
        kconf_code_commits['commit.committer.date'])
    other_commits['commit.committer.date'] = pd.to_datetime(
        other_commits['commit.committer.date'])
    no_change_commits['commit.committer.date'] = pd.to_datetime(
        no_change_commits['commit.committer.date'])

    data = {
        'kconf_def_commit_count': kconf_def_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='ME')])['sha']
            .count(),
        'code_commit_count': code_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='ME')])['sha']
            .count(),
        'kconf_code_commit_count': kconf_code_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='ME')])['sha']
            .count(),
        'other_commit_count': other_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='ME')])['sha']
            .count(),
        'no_change_commit_count': no_change_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='ME')])['sha']
            .count(),
    }
    return data


def commit_count_by_change_type_per_week(project_config):
    kconf_def_commits = read_csv_to_df(project_config.file_kdef_commits)
    code_commits = read_csv_to_df(project_config.file_code_commits)
    kconf_code_commits = read_csv_to_df(project_config.file_kdef_code_commits)
    other_commits = read_csv_to_df(project_config.file_other_commits)
    no_change_commits = read_csv_to_df(project_config.file_no_change_commits)

    kconf_def_commits['commit.committer.date'] = (
        pd.to_datetime(kconf_def_commits['commit.committer.date']) 
        - pd.to_timedelta(7, unit='d'))
    code_commits['commit.committer.date'] = (
        pd.to_datetime(code_commits['commit.committer.date'])
        - pd.to_timedelta(7, unit='d'))
    kconf_code_commits['commit.committer.date'] = (
        pd.to_datetime(kconf_code_commits['commit.committer.date'])
        - pd.to_timedelta(7, unit='d'))
    other_commits['commit.committer.date'] = (
        pd.to_datetime(other_commits['commit.committer.date'])
        - pd.to_timedelta(7, unit='d'))
    no_change_commits['commit.committer.date'] = (
        pd.to_datetime(no_change_commits['commit.committer.date'])
        - pd.to_timedelta(7, unit='d'))

    data = {
        'kconf_def_commit_count': kconf_def_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='W')])['sha']
            .count(),
        'code_commit_count': code_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='W')])['sha']
            .count(),
        'kconf_code_commit_count': kconf_code_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='W')])['sha']
            .count(),
        'other_commit_count': other_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='W')])['sha']
            .count(),
        'no_change_commit_count': no_change_commits.groupby(
            [pd.Grouper(key='commit.committer.date', freq='W')])['sha']
            .count()
    }
    return data


def commit_count_per_year_change_type(project_config):
    kconf_def_commits = read_csv_to_df(project_config.file_kdef_commits)
    code_commits = read_csv_to_df(project_config.file_code_commits)
    kconf_code_commits = read_csv_to_df(project_config.file_kdef_code_commits)
    other_commits = read_csv_to_df(project_config.file_other_commits)
    no_change_commits = read_csv_to_df(project_config.file_no_change_commits)

    kconf_def_commits['commit.committer.date'] = pd.to_datetime(
        kconf_def_commits['commit.committer.date'])
    code_commits['commit.committer.date'] = pd.to_datetime(
        code_commits['commit.committer.date'])
    kconf_code_commits['commit.committer.date'] = pd.to_datetime(
        kconf_code_commits['commit.committer.date'])
    other_commits['commit.committer.date'] = pd.to_datetime(
        other_commits['commit.committer.date'])
    no_change_commits['commit.committer.date'] = pd.to_datetime(
        no_change_commits['commit.committer.date'])

    counts = {
        'kconf_def_commit_count': kconf_def_commits.groupby(
            [kconf_def_commits['commit.committer.date'].dt.year])['sha']
            .count(),
        'code_commit_count': code_commits.groupby(
            [code_commits['commit.committer.date'].dt.year])['sha']
            .count(),
        'kconf_code_commit_count': kconf_code_commits.groupby(
            [kconf_code_commits['commit.committer.date'].dt.year])['sha']
            .count(),
        'other_commit_count': other_commits.groupby(
            [other_commits['commit.committer.date'].dt.year])['sha']
            .count(),
        'no_change_commit_count': no_change_commits.groupby(
            [no_change_commits['commit.committer.date'].dt.year])['sha']
            .count()
    }

    years = commit_count_per_year(project_config)
    years = years.index
    data = {'year': years.tolist()}

    for k, v in counts.items():
        data[k] = [v[y] if y in v.index else 0 for y in years]

    df = pd.DataFrame(data)
    df.to_csv(project_config.file_commit_count_per_year_change_type,
              header=True, index=False)
    return data


def commit_count_per_year_kdef_nonkdef(project_config):
    counts = commit_count_per_year_change_type(project_config)

    data = {}
    data['year'] = counts['year']
    data['kconfig'] = [
        counts['kconf_def_commit_count'][i] + counts['kconf_code_commit_count'][i]
        for i in range(len(counts['year']))
    ]
    data['non_kconfig'] = [
        counts['code_commit_count'][i] + counts['other_commit_count'][i] +
        counts['no_change_commit_count'][i]
        for i in range(len(data['year']))
    ]

    df = pd.DataFrame.from_dict(data)
    df.to_csv(project_config.file_commit_count_per_year_commit_type,
              header=True, index=False)
    return data
