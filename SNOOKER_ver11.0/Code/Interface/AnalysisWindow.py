import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QGroupBox, QPushButton, QHBoxLayout, QLabel, QComboBox, QFileDialog, \
    qApp, QScrollArea, QRadioButton
from qtwidgets import Toggle
import threading

from Code.Classification import Classificator
from Code.Classification.ClassificationVariables import ClassificationVariables
from Code.Classification.Classificator import runClassificator


def changeClassificationMode():
    print("something something")


class MetaAnalysis:
    simpleMF = False


class AnalysisWindow(QObject):
    file = ''

    def __init__(self):
        self.selection_label = None
        self.analysis_layout = None
        self.column_selection = None
        self.columns = []
        self.select_file_button = None
        self.selection = None
        self.metaAnalysisTab = None

    def getFileColumns(self, analysis_layout):
        data = pd.read_csv(self.file, sep=";", index_col=False)
        self.columns = data.columns
        # AnalysisWindow.columnSelectionWidget(self, analysis_layout)

    def changeClassificationObject(self, b, c):
        if b.isChecked():
            if c.text() == 'Simple Meta Features':
                print("Simple MF was activated!")
                ClassificationVariables.simpleMF = True
            if c.text() == 'Statistical Meta Features':
                print("Statistical MF was activated")
                ClassificationVariables.statisticalMF = True
            if c.text() == 'Information Theoretical Meta Features':
                print("Information Theoretical Meta Features activated")
                ClassificationVariables.info_theoMF = True
            if c.text() == 'Model-based Meta Features':
                print("Model-based Meta Features activated")
                ClassificationVariables.modelbasedMF = True
            if c.text() == 'Landmarking Meta Features':
                print("Landmarking Meta Features activated")
                ClassificationVariables.landmarkingMF = True
            if c.text() == 'Relative Landmarking Meta Features':
                print("Relative Landmarking Meta Features activated")
                ClassificationVariables.relative_landmarkingMF = True
            if c.text() == 'Clustering Meta Features':
                print("Clustering Meta Features activated")
                ClassificationVariables.clusteringMF = True
            if c.text() == "Concept Meta Features":
                print("Concept Meta Features activated")
                ClassificationVariables.conceptMF = True
            if c.text() == "Itemset Meta Features":
                print("Itemset Meta Features activated")
                ClassificationVariables.itemsetMF = True
            if c.text() == 'Complexity Meta Features':
                print("Complexity Meta Features activated")
                ClassificationVariables.complexityMF = True
        else:
            if c.text() == 'Simple Meta Features':
                print("Simple Mf not activated!")
                ClassificationVariables.simpleMF = False
            if c.text() == 'Statistical Meta Features':
                print("Statistical MF not activated")
                ClassificationVariables.statisticalMF = False
            if c.text() == 'Information Theoretical Meta Features':
                print("Information Theoretical Meta Features deactivated")
                ClassificationVariables.statisticalMF = False
            if c.text() == 'Model-based Meta Features':
                print("Model-based Meta Features deactivated")
                ClassificationVariables.modelbasedMF = False
            if c.text() == 'Landmarking Meta Features':
                print("Landmarking Meta Features deactivated")
                ClassificationVariables.landmarkingMF = False
            if c.text() == 'Relative Landmarking Meta Features':
                print("Relative Landmarking Meta Features deactivated")
                ClassificationVariables.relative_landmarkingMF = False
            if c.text() == 'Clustering Meta Features':
                print("Clustering Meta Features deactivated")
                ClassificationVariables.clusteringMF = False
            if c.text() == 'Concept Meta Features':
                print("Concept Meta Features deactivated")
                ClassificationVariables.conceptMF = False
            if c.text() == 'Itemset Meta Features':
                print("Itemset Meta Features deactivated")
                ClassificationVariables.itemsetMF = False
            if c.text() == 'Complexity Meta Features':
                print("Complexity Meta Features deactivated")
                ClassificationVariables.complexityMF = False

    def columnSelectionWidget(self, analysis_layout):

        # columns_layout = QScrollArea()
        # self.scroll_content = QWidget()
        # self.scroll_content_layout = QVBoxLayout()
        # self.scroll_content.setLayout(self.scroll_content_layout)
        # self.scroll.setWidgetResizable(True)
        # self.scroll.setWidget(self.scroll_content)

        columns_layout = QHBoxLayout()
        column_selection = QGroupBox("Column selection:", self)
        column_selection.setFont(self.features_font)
        aux = 1
        for column in self.columns:
            print(column)
            column_name = QLabel(column)
            column_name.setWordWrap(True)
            # column_display.addWidget(column_name, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            column_selection.addWidget(column_name, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # self.column_selection.setLayout(columns_layout)
            # QWidget.update(self.column_selection)
            #
            # self.metaAnalysisTab.setLayout(analysis_layout)

        # columns_layout.update()
        analysis_layout.addLayout(columns_layout)
        # analysis_layout.addLayout(column_selection)
        analysis_layout.update()

    def dialog(self, analysis_layout):
        # directory should be changed according to the machine this project is running in
        directory = '/Users/joaolemos/DatasetGen/Output/Generation'
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", directory,
                                                  "All Files (*);;Python Files (*.py);;Text Files (*.txt)")
        if check:
            AnalysisWindow.file = file
            print(file)
            #AnalysisWindow.getFileColumns(self, analysis_layout)

    def on_click(self):
        print('Button pressed')
        AnalysisWindow.dialog(self)

    def loadClassificationModes(self, analysis_layout):

        classification_layout = QVBoxLayout()
        self.classification = QGroupBox("Metafeature Classification Selection:", self)
        self.classification.setFont(self.features_font)

        simple_mf_layout = QHBoxLayout()
        self.simple_mf_label = QLabel("Simple Meta Features")
        self.simple_mf_toggle = Toggle()
        self.simple_mf_label.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.simple_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.simple_mf_toggle.stateChanged \
            .connect(lambda:
                     AnalysisWindow.changeClassificationObject(self,
                                                               self.simple_mf_toggle,
                                                               self.simple_mf_label
                                                               ))
        simple_mf_layout.addWidget(self.simple_mf_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        simple_mf_layout.addWidget(self.simple_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(simple_mf_layout)

        statistical_mf_layout = QHBoxLayout()
        self.statistical_mf_label = QLabel("Statistical Meta Features")
        self.statistical_mf_toggle = Toggle()
        self.statistical_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.statistical_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.statistical_mf_toggle,
                                                                       self.statistical_mf_label
                                                                       ))
        statistical_mf_layout.addWidget(self.statistical_mf_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        statistical_mf_layout.addWidget(self.statistical_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(statistical_mf_layout)

        info_theo_mf_layout = QHBoxLayout()
        self.info_theo_mf_label = QLabel("Information Theoretical Meta Features")
        self.info_theo_mf_toggle = Toggle()
        self.info_theo_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.info_theo_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.info_theo_mf_toggle,
                                                                       self.info_theo_mf_label
                                                                       ))
        info_theo_mf_layout.addWidget(self.info_theo_mf_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        info_theo_mf_layout.addWidget(self.info_theo_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(info_theo_mf_layout)

        model_based_mf_layout = QHBoxLayout()
        self.model_based_mf_label = QLabel("Model-based Meta Features")
        self.model_based_mf_toggle = Toggle()
        self.model_based_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.model_based_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.model_based_mf_toggle,
                                                                       self.model_based_mf_label
                                                                       ))
        model_based_mf_layout.addWidget(self.model_based_mf_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        model_based_mf_layout.addWidget(self.model_based_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(model_based_mf_layout)

        landmarking_mf_layout = QHBoxLayout()
        self.landmarking_mf_label = QLabel("Landmarking Meta Features")
        self.landmarking_mf_toggle = Toggle()
        self.landmarking_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.landmarking_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.landmarking_mf_toggle,
                                                                       self.landmarking_mf_label
                                                                       ))
        landmarking_mf_layout.addWidget(self.landmarking_mf_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        landmarking_mf_layout.addWidget(self.landmarking_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(landmarking_mf_layout)

        relative_landmarking_mf_layout = QHBoxLayout()
        self.relative_landmarking_mf_label = QLabel("Relative Landmarking Meta Features")
        self.relative_landmarking_mf_toggle = Toggle()
        self.relative_landmarking_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.relative_landmarking_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.relative_landmarking_mf_toggle,
                                                                       self.relative_landmarking_mf_label
                                                                       ))
        relative_landmarking_mf_layout.addWidget(self.relative_landmarking_mf_label,
                                                 alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        relative_landmarking_mf_layout.addWidget(self.relative_landmarking_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(relative_landmarking_mf_layout)

        clustering_mf_layout = QHBoxLayout()
        self.clustering_mf_label = QLabel("Clustering Meta Features")
        self.clustering_mf_toggle = Toggle()
        self.clustering_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.clustering_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.clustering_mf_toggle,
                                                                       self.clustering_mf_label
                                                                       ))
        clustering_mf_layout.addWidget(self.clustering_mf_label,
                                       alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        clustering_mf_layout.addWidget(self.clustering_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(clustering_mf_layout)

        concept_mf_layout = QHBoxLayout()
        self.concept_mf_label = QLabel("Concept Meta Features")
        self.concept_mf_toggle = Toggle()
        self.concept_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.concept_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.concept_mf_toggle,
                                                                       self.concept_mf_label
                                                                       ))
        concept_mf_layout.addWidget(self.concept_mf_label,
                                    alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        concept_mf_layout.addWidget(self.concept_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(concept_mf_layout)

        itemset_mf_layout = QHBoxLayout()
        self.itemset_mf_label = QLabel("Itemset Meta Features")
        self.itemset_mf_toggle = Toggle()
        self.itemset_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.itemset_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.itemset_mf_toggle,
                                                                       self.itemset_mf_label
                                                                       ))
        itemset_mf_layout.addWidget(self.itemset_mf_label,
                                    alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        itemset_mf_layout.addWidget(self.itemset_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(itemset_mf_layout)

        complexity_mf_layout = QHBoxLayout()
        self.complexity_mf_label = QLabel("Complexity Meta Features")
        self.complexity_mf_toggle = Toggle()
        self.complexity_mf_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.complexity_mf_toggle.stateChanged \
            .connect(lambda: AnalysisWindow.changeClassificationObject(self,
                                                                       self.complexity_mf_toggle,
                                                                       self.complexity_mf_label
                                                                       ))
        complexity_mf_layout.addWidget(self.complexity_mf_label,
                                       alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        complexity_mf_layout.addWidget(self.complexity_mf_toggle, alignment=Qt.AlignLeft)
        classification_layout.addLayout(complexity_mf_layout)

        self.classification.setLayout(classification_layout)
        analysis_layout.addWidget(self.classification)

    def runClassification(self):

        if AnalysisWindow.file != '':
            print(AnalysisWindow.file)
            print(ClassificationVariables)
            runClassificator(AnalysisWindow.file)
            #Classificator.runClassificator(AnalysisWindow.file)
        else:
            print("no file selected")

    def checkClassification(self, analysis_layout):

        button_layout = QVBoxLayout()
        self.classification_button = QPushButton("Run Analysis", self)
        self.classification_button.setObjectName('classificationButton')
        self.classification_button.setProperty('ready', True)
        self.classification_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.classification_button.clicked.connect(AnalysisWindow.runClassification)
        button_layout.addWidget(self.classification_button, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        analysis_layout.addWidget(self.classification_button)

    def metaAnalysisTab(self):

        analysis_layout = QVBoxLayout()
        self.metaAnalysisTab = QWidget()

        self.columns = []
        self.metaAnalysisTab.resize(self.metaAnalysisTab.sizeHint())
        AnalysisWindow.selectFile(self, analysis_layout)
        # AnalysisWindow.columnSelectionWidget(self, analysis_layout)

        # analysis_layout.addWidget(self.classification)
        AnalysisWindow.loadClassificationModes(self, analysis_layout)

        AnalysisWindow.checkClassification(self, analysis_layout)

        self.metaAnalysisTab.setLayout(analysis_layout)

        return self.metaAnalysisTab

    # Set up dataset file path:
    def selectFile(self, analysis_layout):

        selection_div = QHBoxLayout()
        selection_label = QLabel("File selection:")

        select_file_button = QPushButton()
        select_file_button.setText("Select File")
        select_file_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        select_file_button.clicked.connect(lambda: AnalysisWindow.dialog(self, analysis_layout))
        # select_file_button.setText(AnalysisWindow.file)

        # select_file_button_layout.addWidget(select_file_button)
        selection_div.addWidget(selection_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        selection_div.addWidget(select_file_button, alignment=Qt.AlignLeft)

        analysis_layout.addLayout(selection_div)

    def getDataColumns(self):
        return self.columns
