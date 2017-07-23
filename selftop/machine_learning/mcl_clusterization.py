import os
import tempfile

TRANSITION_MATRIX_DURATION_THRESHOLD = 15

# Paths to binary
# See https://micans.org/mcl/
BIN_MCXLOAD = 'mcxload'
BIN_MCL = 'mcl'
BIN_MCXDUMP = 'mcxdump'


def mcl_clusters(matrix):
    """Returns window_id => claster_label dict
    :type matrix: {}
    :param matrix:  Transition matrix. Number of trasition from one window to other.
                    Dict with index of type (winId, winId) and values is transtion number
    :return: {}
    """

    # Prepare paths
    _, file_data_path = tempfile.mkstemp(None, 'selftop_data')
    _, file_mci_path = tempfile.mkstemp()
    _, file_tab_path = tempfile.mkstemp()
    _, file_cluster_native_path = tempfile.mkstemp()
    _, file_cluster_path = tempfile.mkstemp()
    file_data = open(file_data_path, 'w')
    for idx, value2 in matrix.items():
        file_data.write('{}\t{}\t{}\n'.format(idx[0], idx[1], matrix[idx]))
    file_data.close()

    # Build command line
    cmd = "{mcxload} " \
          " --stream-mirror" \
          " -abc {file_data_path}" \
          " -o {file_mci_path}" \
          " -write-tab {file_tab_path}" \
          " && {mcl}" \
          " {file_mci_path}" \
          " -o {file_cluster_native_path}" \
          " && {mcxdump}" \
          " -icl {file_cluster_native_path}" \
          " -tabr {file_tab_path}" \
          " -o {file_cluster_path}".format(
        file_data_path=file_data_path,
        file_mci_path=file_mci_path,
        file_tab_path=file_tab_path,
        file_cluster_native_path=file_cluster_native_path,
        file_cluster_path=file_cluster_path,
        mcxload=BIN_MCXLOAD,
        mcl=BIN_MCL,
        mcxdump=BIN_MCXDUMP
    )

    # execute command and get result
    os.system(cmd)
    class_label = 0
    mcl_cluster_map = {}
    with open(file_cluster_path, 'r') as file:
        for line in file:
            for window_id in line.split('\t'):
                mcl_cluster_map[int(window_id)] = str(class_label)
            class_label += 1

    # cleanup
    os.remove(file_data_path)
    os.remove(file_mci_path)
    os.remove(file_tab_path)
    os.remove(file_cluster_native_path)
    os.remove(file_cluster_path)

    return mcl_cluster_map


def buildTransitionMatrix(records):
    useful_records = [x for x in records if
                      x['duration'] >= TRANSITION_MATRIX_DURATION_THRESHOLD]
    # Build trasition matrix
    matrix = {}
    if len(useful_records) != 0:
        prev = useful_records[0]
        for curr in useful_records[1:]:
            index = (prev['window_id'], curr['window_id'])
            if index not in matrix:
                matrix[index] = 0
            matrix[index] += 1
            prev = curr

    return matrix
