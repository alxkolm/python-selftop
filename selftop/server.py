from __future__ import absolute_import
from datetime import date
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

    titles = set([record['window_title'] for record in records if record['window_title'] != ''])
    cluster_map = get_title_clusters(titles)

    useful_windows = [x for x in records if x['duration'] >= TRANSITION_MATRIX_DURATION_THRESHOLD]
    matrix = {}
    prev = useful_windows[0]
    for curr in useful_windows[1:]:
        idx = (prev['window_id'], curr['window_id'])
        if idx not in matrix:
            matrix[idx] = 0
        matrix[idx] += 1
        prev = curr



    return {'processes': processes, 'windows': windows, 'records': records, 'titleClusters': cluster_map}


def get_title_clusters(titles):
    titles_cluster_labels = string_clusterization.run(list(titles))
    cluster_map = {str(x[0]): int(x[1]) for x in
                   zip(titles, titles_cluster_labels)}
    return cluster_map


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
    GROUP BY window.title
    """
    windows = [dict(x) for x in cur.execute(sql).fetchall()]
    return windows


def get_processes():
    sql = """ SELECT id, name, alias FROM process """
    processes = [dict(x) for x in cur.execute(sql).fetchall()]
    return processes


run(host='localhost', port=8080, debug=True, reloader=True)
