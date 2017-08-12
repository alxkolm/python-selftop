import sqlite3

import bottle

import selftop.machine_learning.mcl_clusterization as mcl_clusterization
import selftop.machine_learning.record_clusterization as record_clusterization
import selftop.data


app = bottle.app()
EXCLUDED_WINDOWS = [661]

@app.route('/')
def index():
    processes = selftop.data.get_processes()

    windows = selftop.data.get_windows()

    records = selftop.data.get_records()

    titles = {record['window_id']: record['window_title'] for record in records
              if record['window_title'] != ''}
    cluster_map = selftop.data.get_title_clusters(titles)

    records_filtered = [record for record in records if
               record['window_id'] not in EXCLUDED_WINDOWS and record['window_title'] != '']

    mcl_cluster_map = mcl_clusterization.mcl_clusters(
        mcl_clusterization.buildTransitionMatrix(records_filtered))

    records_cluster_map = record_clusterization.run(records, mcl_cluster_map, cluster_map)

    return {'processes': processes, 'windows': windows, 'records': records,
            'titleClusters': cluster_map, 'mclClusters': mcl_cluster_map, 'recordClusters': records_cluster_map}


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
