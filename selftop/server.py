import sqlite3
from datetime import date

import bottle

import selftop.machine_learning.string_clusterization as string_clusterization
import selftop.machine_learning.mcl_clusterization as mcl_clusterization

DB_STRING = '/home/alexey.kolmakov/.selftop/selftop.db'
db = sqlite3.connect(DB_STRING)
db.row_factory = sqlite3.Row
cur = db.cursor()
app = bottle.app()


@app.route('/')
def index():
    processes = get_processes()

    windows = get_windows()

    records = get_records()

    titles = {record['window_id']: record['window_title'] for record in records
              if record['window_title'] != ''}
    cluster_map = get_title_clusters(titles)

    mcl_cluster_map = mcl_clusterization.mcl_clusters(
        mcl_clusterization.buildTransitionMatrix(records))

    return {'processes': processes, 'windows': windows, 'records': records,
            'titleClusters': cluster_map, 'mclClusters': mcl_cluster_map}


def get_title_clusters(titles):
    """Returns window_id => claster_label dict"""
    keys = list(titles.keys())
    values = list(titles.values())
    titles_set = list(set(titles.values()))
    titles_cluster_labels = string_clusterization.run(titles_set)

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
        SUM(duration / 1000) as time,
        SUM(motions) as motions,
        SUM(motions_filtered) as motions_filtered,
        SUM(clicks) as clicks,
        SUM(scrolls) as scrolls,
        SUM(keys) as keys
    FROM window
    JOIN record on window.id = record.window_id
    WHERE record.start >= ?
    GROUP BY window.id
    """
    windows = [dict(x) for x in cur.execute(sql, [date.today()]).fetchall()]
    return windows


def get_processes():
    sql = """ SELECT id, name, alias FROM process """
    processes = [dict(x) for x in cur.execute(sql).fetchall()]
    return processes


class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


if __name__ == '__main__':
    app.install(EnableCors())
    app.run(host='localhost', port=9999, debug=True, reloader=True)
