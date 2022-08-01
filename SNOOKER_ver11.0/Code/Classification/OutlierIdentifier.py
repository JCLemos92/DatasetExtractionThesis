from datetime import datetime
from pymfe.mfe import MFE
from sklearn.datasets import load_iris
from timeit import default_timer as timer
from datetime import timedelta

import pandas as pd
import numpy as np

from Code.ClassificationVariables import ClassificationVariables

class OutlierIdentifier:

    def statistical_outlier(path):
        f = open("../../Output/Analysis/StatisticalOutlier.txt", "a+")
        f.write(f'\nAnalysis of file {path}.\n')
        f.close()

        metafeatures = ["can_cor", "cor", "cov", "eigenvalues", "g_mean", "gravity", "h_mean",
                        "iq_range", "kurtosis", "lh_trace", "mad", "max", "mean", "median", "min",
                        "nr_cor_attr", "nr_disc", "nr_norm", "nr_outliers", "p_trace", "range",
                        "roy_root", "sd", "sd_ratio", "skewness", "sparsity", "t_mean", "var", "w_lambda"]

        df = pd.read_csv(path, sep=";", index_col=False)

        for i in metafeatures:
            f = open("../../Output/Analysis/StatisticalOutlier.txt", "a+")
            start = timer()
            X, y = df.drop('ID', axis=1), df['ID']

            mfe = MFE(features=[i])
            mfe.fit(X.values, y.values)
            ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
            f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

            end = timer()
            print(f'{i} took {timedelta(seconds=end - start)}.\n')
            f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')
            f.close()

    path = ['../../Datasets/CausesOfDeath_France_2001-2008.csv',
            '../../Output/Generation/Speed_generaton.csv',
            '../../Output/Generation/Queue_generation.csv', '../../Output/Generation/test.csv']

    for j in path:
        statistical_outlier(j)