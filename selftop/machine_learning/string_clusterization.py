import numpy as np
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MeanShift, estimate_bandwidth


def run(titles):
    # extract feature
    vectorizer = TfidfVectorizer()
    x_train = vectorizer.fit_transform(titles)

    # clustering
    estimator = KMeans(n_clusters=int(len(titles) / 5))
    labels = estimator.fit_predict(x_train)
    return labels
