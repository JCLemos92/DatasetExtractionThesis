# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 10:49:57 2021

@author: Leonardo Ferreira
@goal: Useful functions for the interfaces used
"""

import string
from datetime import datetime
import os
import random
import os.path
import sys

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTime
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QSizePolicy,
    QLabel,
    QTimeEdit, 
    QMainWindow,
    QScrollArea,
    QTabWidget,
    QDesktopWidget,
    QPushButton,
    QRadioButton,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QComboBox,
    QSlider,
    QProgressBar,
    QDateTimeEdit,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
)

class InterfaceUtils:
    
    # Sets the fonts used in the interface
    def setFonts(self):
        self.main_font = QtGui.QFont(str("Initial Font"), 10)
        self.main_font.setBold(True)
        self.features_font = QtGui.QFont(str(self.main_font), 8)
        self.features_font.setBold(True) 
        
    # The messageBox appears with specific title and content
    def message(self, title, content):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowIcon(QtGui.QIcon('./Resources//tkinter_icon.ico'))   
        msg.setText(content)         
        msg.exec_()
    
    # Sets the style used in the interface
    def widgetsSetStyle(self, path): 
        with open(path,"r") as fh:
            self.setStyleSheet(fh.read())
            
    # Gets the team of an analyst
    def getTeamAnalyst(self, teams, name):
        for team in teams.keys():
            if name in teams[team]['analysts']:
                return team   
            
    def updateSizes(self, index):
        
        #print(index)
        for i in range(self.tabs.count()):
            if i != index:
                self.tabs.widget(i).setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        self.tabs.widget(index).setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.tabs.widget(index).resize(self.tabs.widget(index).minimumSizeHint())
        self.tabs.widget(index).adjustSize()
        
        for i in range(0,20):
            QApplication.processEvents()
        #print("Aqui", self.minimumSizeHint())
        self.resize(self.minimumSizeHint())
        