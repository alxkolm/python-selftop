import numpy as np
from kmodes import kmodes
from kmodes import kprototypes
import dateutil.parser

def run(records, mcl_clusters, title_clusters):
    output = []
    for record in records:
        output.append((
            'title_' + str(title_clusters[record['window_id']] if record['window_id'] in title_clusters else -1),
            'mcl_' + str(mcl_clusters[record['window_id']] if record['window_id'] in mcl_clusters else -1),
            'pid' + str(record['process_id']),
            dateutil.parser.parse(record['start']).hour
        ))
    # km4 = kmodes.KModes(n_clusters=4, init='Huang', n_init=5, verbose=1)
    # km5 = kmodes.KModes(n_clusters=5, init='Huang', n_init=5, verbose=1)
    # km6 = kmodes.KModes(n_clusters=10, init='Huang', n_init=5, verbose=1)
    kp10 = kprototypes.KPrototypes(n_clusters=10, init='Cao', verbose=2)
    X = np.array(output)
    T = X
    # clusters4 = km4.fit_predict(T)
    # clusters5 = km5.fit_predict(T)
    # clusters6 = km6.fit_predict(T)
    clusters6 = kp10.fit_predict(T, categorical=[0,1,2])

    record_ids = [r['id'] for r in records]
    map = {recordId:str(cluster) for recordId, cluster in zip(record_ids,list(clusters6))}
    return map
