import threading
from datetime import datetime
from pymfe.mfe import MFE
from sklearn.datasets import load_iris
from timeit import default_timer as timer
from datetime import timedelta

import os
import pandas as pd
import numpy as np

from Code.Classification.ClassificationVariables import ClassificationVariables


class DataColumn(object):

    def __int__(self, name, data_type):
        self.name = name
        self.data_type = data_type

    def get_name(self):
        return self.name


def runClassificator(path):
    # df = pd.read_csv(file, sep=";", index_col=False)

    # if ClassificationVariables.simpleMF:
    # path = '../../Output/Generation/Speed_generaton.csv'
    # path = '../../Output/Generation/generatedDataset.csv.csv'

    #df = pd.read_csv(path, sep=";", index_col=False)

    pathAux = '../../Output/Generation/'

    # Check whether the specified path exists or not
    isExist = os.path.exists(pathAux)

    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(pathAux)
        print("The new directory is created!")

    pathAux = 'Output/MetaAnalysis'
    isExist = os.path.exists(pathAux)

    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(pathAux)
        print("The new directory is created!")

    simpleMfTrhead = Classificator.simple_meta_analysis(path)

    print("Starting analysis of meta-features in file " + path)
    analysis_counter = 0
    if ClassificationVariables.simpleMF:
        print('Starting Simple Meta Features Analysis')
        #Classificator.simple_meta_analysis(path)
        simpleMfTrhead.start()
        analysis_counter += 1
    if ClassificationVariables.statisticalMF:
        print('Starting Statistical Meta Features Analysis')
        Classificator.statistical_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.info_theoMF:
        print('Starting Information Theoretical Meta Features Analysis')
        Classificator.info_theo_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.modelbasedMF:
        print('Starting Model-Based Meta Features Analysis')
        Classificator.model_based_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.landmarkingMF:
        print('Starting Landmarking Meta Features Analysis')
        Classificator.landmarking_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.relative_landmarkingMF:
        print('Starting Relative Landmarking Meta Features Analysis')
        Classificator.relative_landmarking_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.clusteringMF:
        print('Starting Clustering Meta Features Analysis')
        Classificator.clustering_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.conceptMF:
        print('Starting Concept Meta Features Analysis')
        Classificator.concept_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.itemsetMF:
        print('Starting Itemset Meta Features Analysis')
        Classificator.itemset_meta_analysis(path)
        analysis_counter += 1
    if ClassificationVariables.complexityMF:
        print('Starting Complexity Meta Features Analysis')
        Classificator.complexity_meta_analysis(path)
        analysis_counter += 1

    print("Analysis made to file " + path + ". " + str(analysis_counter) + " meta-feature families analyzed")


class Classificator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def simple_meta_analysis(path):
        print(path)
        start = timer()

        f = open('Output/MetaAnalysis/SimpleMetaFeatures.txt', "w+")

        f.write(f'Simple MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        # Extract all general measures
        mfe = MFE(
            # groups="all",
            # summary="all"
            groups=["general"],
        )

        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')
        f.close()
        print('Simple meta-feature analysis complete')

    def statistical_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/StatisticalMetaFeatures.txt", "w+")

        f.write(f'Statistical MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["statistical"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Statistical meta-feature analysis complete')

    def info_theo_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/InformationTheoreticalMetaFeatures.txt", "w+")

        f.write(f'Information Theoretical MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["info-theory"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Information Theoretical meta-feature analysis complete')

    def model_based_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/ModelBasedMetaFeatures.txt", "w+")

        f.write(f'Model Based MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["model-based"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Model Based meta-feature analysis complete')

    def landmarking_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/LandmarkingMetaFeatures.txt", "w+")

        f.write(f'Landmarking MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["landmarking"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Landmarking meta-feature analysis complete')

    def relative_landmarking_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/RelativeLandmarkingMetaFeatures.txt", "w+")

        f.write(f'Relative Landmarking MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["relative"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        timelapse = end - start
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Relative Landmarking meta-feature analysis complete')

    def clustering_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/ClusteringMetaFeatures.txt", "w+")

        f.write(f'Clustering MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["clustering"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Clustering meta-feature analysis complete')

    def concept_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/ConceptMetaFeatures.txt", "w+")

        f.write(f'Concept MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["concept"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Concept meta-feature analysis complete')

    def itemset_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/ItemsetMetaFeatures.txt", "w+")

        f.write(f'Itemset MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["itemset"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Itemset meta-feature analysis complete')

    def complexity_meta_analysis(path):
        start = timer()

        f = open("Output/MetaAnalysis/ComplexityMetaFeatures.txt", "w+")

        f.write(f'Complexity MetaFeature Analysis of file in {path} at {datetime.now()}.\n')

        df = pd.read_csv(path, sep=";", index_col=False)

        X, y = df.drop('ID', axis=1), df['ID']

        mfe = MFE(
            groups=["complexity"],
        )
        mfe.fit(X.values, y.values)
        ft = mfe.extract(cat_cols='auto', suppress_warnings=True)
        f.write("\n".join("{:50} {:30}".format(x, y) for x, y in zip(ft[0], ft[1])))

        end = timer()
        f.write(f'\nAnalysis took {timedelta(seconds=end - start)}.\n')

        f.close()
        print('Complexity meta-feature analysis complete')

    # complexity_meta_analysis(path)
