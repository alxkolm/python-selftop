import selftop.machine_learning as ml
import selftop.data
import selftop.machine_learning.mcl_clusterization as mcl_clusterization
from datetime import date
import csv
import os
from kmodes import kprototypes, kmodes
import numpy as np
import pandas as pd


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
      end,
      record.*
    FROM record
      LEFT JOIN window ON window.id = record.window_id
      LEFT JOIN process ON process.id = window.process_id
    WHERE duration > 0
    AND start >= ?
    ORDER BY start;
    """
    records = [dict(x) for x in selftop.data.cur.execute(sql, [date.today()]).fetchall()]

    return records


processes = selftop.data.get_processes()

windows = selftop.data.get_windows()

records = get_records()

titles = {record['window_id']: record['window_title'] for record in records
          if record['window_title'] != ''}
cluster_map = selftop.data.get_title_clusters(titles)

mcl_cluster_map = mcl_clusterization.mcl_clusters(
    mcl_clusterization.buildTransitionMatrix(records))

# compile dataset
a=1
output = []
for record in records:
    output.append((
        'title_' + str(cluster_map[record['window_id']] if record['window_id'] in cluster_map else -1),
        'mcl_' + str(mcl_cluster_map[record['window_id']] if record['window_id'] in mcl_cluster_map else -1),
        'pid' + str(record['process_id']),
        record['keys'],
        record['clicks'],
        record['scrolls'],
        record['motions'],
        record['motions_filtered'],
    ))

kproto = kprototypes.KPrototypes(n_clusters=4, init='Cao', verbose=2)
km4 = kmodes.KModes(n_clusters=4, init='Huang', n_init=5, verbose=1)
km5 = kmodes.KModes(n_clusters=5, init='Huang', n_init=5, verbose=1)
km6 = kmodes.KModes(n_clusters=6, init='Huang', n_init=5, verbose=1)
X = np.array(output)
T = X[:,0:3]
clusters4 = km4.fit_predict(T, categorical=[0, 1, 2])
clusters5 = km5.fit_predict(T, categorical=[0, 1, 2])
clusters6 = km6.fit_predict(T, categorical=[0, 1, 2])

Z = np.hstack((T, np.reshape(clusters4, (-1,1)), np.reshape(clusters5, (-1,1)),np.reshape(clusters6, (-1,1))))
# pd.DataFrame(Z).to_csv('output/records.csv', index=False, header=['titleCluster', 'mclCluster', 'pid', 'keys', 'clicks', 'scrolls', 'motions', 'motions_filtered', 'catCluster'])
pd.DataFrame(Z).to_csv('output/records.csv', index=False, header=['titleCluster', 'mclCluster', 'pid', 'catCluster4', 'catCluster5', 'catCluster6'])
# np.savetxt('output/records.csv', Z, delimiter=',', header=','.join(['titleCluster', 'mclCluster', 'pid', 'keys', 'clicks', 'scrolls', 'motions', 'motions_filtered', 'catCluster']))

# with open('output/records.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerow(['titleCluster', 'mclCluster', 'pid', 'keys', 'clicks', 'scrolls', 'motions', 'motions_filtered'])
#     writer.writerows(output)
a=2



