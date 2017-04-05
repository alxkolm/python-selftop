from __future__ import absolute_import
import os
from datetime import date
import tempfile
import subprocess
import sqlite3
from bottle import route, run
import selftop.machine_learning.string_clusterization as string_clusterization

DB_STRING = '/home/alx/.selftop/selftop.db'
TRANSITION_MATRIX_DURATION_THRESHOLD = 5
db = sqlite3.connect(DB_STRING)
db.row_factory = sqlite3.Row
cur = db.cursor()


@route('/')
def index():
    processes = get_processes()

    windows = get_windows()

    records = get_records()

    titles = {record['window_id']: record['window_title'] for record in records
              if record['window_title'] != ''}
    cluster_map = get_title_clusters(titles)

    mcl_cluster_map = mcl_clusters(records)

    return {'processes': processes, 'windows': windows, 'records': records,
            'titleClusters': cluster_map, 'mclClusters': mcl_cluster_map}


def mcl_clusters(records):
    """Returns window_id => claster_label dict"""
    useful_windows = [x for x in records if
                      x['duration'] >= TRANSITION_MATRIX_DURATION_THRESHOLD]
    matrix = {}
    prev = useful_windows[0]
    for curr in useful_windows[1:]:
        idx = (prev['window_id'], curr['window_id'])
        if idx not in matrix:
            matrix[idx] = 0
        matrix[idx] += 1
        prev = curr
    _, file_data_path = tempfile.mkstemp(None, 'selftop_data')
    _, file_mci_path = tempfile.mkstemp()
    _, file_tab_path = tempfile.mkstemp()
    _, file_cluster_native_path = tempfile.mkstemp()
    _, file_cluster_path = tempfile.mkstemp()
    file_data = open(file_data_path, 'w')
    for idx, value2 in matrix.items():
        file_data.write('{}\t{}\t{}\n'.format(idx[0], idx[1], matrix[idx]))
    file_data.close()
    cmd = "mcxload " \
          " --stream-mirror" \
          " -abc {file_data_path}" \
          " -o {file_mci_path}" \
          " -write-tab {file_tab_path}" \
          " && mcl" \
          " {file_mci_path}" \
          " -o {file_cluster_native_path}" \
          " && mcxdump" \
          " -icl {file_cluster_native_path}" \
          " -tabr {file_tab_path}" \
          " -o {file_cluster_path}".format(
            file_data_path=file_data_path,
            file_mci_path=file_mci_path,
            file_tab_path=file_tab_path,
            file_cluster_native_path=file_cluster_native_path,
            file_cluster_path=file_cluster_path
            )
    os.system(cmd)
    class_label = 0
    mcl_cluster_map = {}
    with open(file_cluster_path, 'r') as file:
        for line in file:
            for window_id in line.split('\t'):
                mcl_cluster_map[int(window_id)] = str(class_label)
            class_label += 1
    os.remove(file_data_path)
    os.remove(file_mci_path)
    os.remove(file_tab_path)
    os.remove(file_cluster_native_path)
    os.remove(file_cluster_path)
    return mcl_cluster_map


def get_title_clusters(titles):
    """Returns window_id => claster_label dict"""
    keys = list(titles.keys())
    values = list(titles.values())
    titles_set = list(set(titles.values()))
    titles_cluster_labels = string_clusterization.run(titles_set)
    cluster_map = {str(x[0]): int(x[1]) for x in
                   zip(titles_set, titles_cluster_labels)}

    def get_id_by_title(title_str):
        return [keys[idx] for idx, v in enumerate(values) if v == title_str]

    out = {}
    for title, label in zip(titles_set, titles_cluster_labels):
        for i in get_id_by_title(title):
            out[i] = str(label)

    return out


def get_records():
    sql = """
    SELECT
      record.id,
      window.id                AS window_id,
      window.title             AS window_title,
      process.id               AS process_id,
      process.name             AS process_name,
      record.duration / 1000.0 AS duration,
      start,
      end
    FROM record
      LEFT JOIN window ON window.id = record.window_id
      LEFT JOIN process ON process.id = window.process_id
    WHERE duration > 0
    AND start >= ?
    ORDER BY start;
    """
    records = [dict(x) for x in cur.execute(sql, [date.today()]).fetchall()]

    return records


def get_windows():
    sql = """
    SELECT
        window.*,
        SUM(duration) as time,
        SUM(motions) as motions,
        SUM(motions_filtered) as motions_filtered,
        SUM(clicks) as clicks,
        SUM(scrolls) as scrolls,
        SUM(keys) as keys
    FROM window
    JOIN record on window.id = record.window_id
    WHERE record.start >= ?
    GROUP BY window.title
    """
    windows = [dict(x) for x in cur.execute(sql, [date.today()]).fetchall()]
    return windows


def get_processes():
    sql = """ SELECT id, name, alias FROM process """
    processes = [dict(x) for x in cur.execute(sql).fetchall()]
    return processes


run(host='localhost', port=8080, debug=True, reloader=True)
