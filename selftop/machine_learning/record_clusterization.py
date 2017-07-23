import numpy as np
from kmodes import kmodes


def run(records, mcl_clusters, title_clusters):
    output = []
    for record in records:
        output.append((
            'title_' + str(title_clusters[record['window_id']] if record['window_id'] in title_clusters else -1),
            'mcl_' + str(mcl_clusters[record['window_id']] if record['window_id'] in mcl_clusters else -1),
            'pid' + str(record['process_id'])
        ))
    # km4 = kmodes.KModes(n_clusters=4, init='Huang', n_init=5, verbose=1)
    # km5 = kmodes.KModes(n_clusters=5, init='Huang', n_init=5, verbose=1)
    km6 = kmodes.KModes(n_clusters=6, init='Huang', n_init=5, verbose=1)
    X = np.array(output)
    T = X
    # clusters4 = km4.fit_predict(T)
    # clusters5 = km5.fit_predict(T)
    clusters6 = km6.fit_predict(T)

    record_ids = [r['id'] for r in records]
    map = {recordId:str(cluster) for recordId,cluster in zip(record_ids,list(clusters6))}
    return map
