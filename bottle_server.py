from bottle import route, run
import sqlite3

DB_STRING = '/home/alx/.selftop/selftop.db'


@route('/')
def index():
    db = sqlite3.connect(DB_STRING)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    sql = """ SELECT id, name, alias FROM process """
    processes = [dict(x) for x in cur.execute(sql).fetchall()]

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
    ORDER BY start;
    """
    records = [dict(x) for x in cur.execute(sql).fetchall()]

    # TODO Keys activity data

    return {'processes': processes, 'windows': windows, 'records': records}

run(host='localhost', port=8080, debug=True, reloader=True)
