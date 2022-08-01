# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 12:16:30 2020

@author: leonardo Ferreira
@goal: Generator Main's Interface
"""

from Code.Interface.AnalysisWindow import AnalysisWindow
from Code.Variables import Variables
from Code.Configurator import Configurator
from SubWindow import SubWindow
from CheckableComboBox import CheckableComboBox 
from InterfaceUtils import InterfaceUtils 
from Code.Utils import Utils
import Code.Generator.DatasetAnalyser 
import Code.Generator.DatasetGenerator

import string
from datetime import datetime
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTime
from PyQt5 import QtGui, QtCore
from qtwidgets import Toggle
import os
import random
import os.path
import sys
#import csv
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    #QSizePolicy,
    QLabel,
    QTimeEdit, 
    QMainWindow,
    QScrollArea,
    QCheckBox,
    #QToolBar,
    QTabWidget,
    QAction,
    QDesktopWidget,
    #QToolButton,
    QPushButton,
    QRadioButton,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QSlider,
    #QProgressBar,
    QDateTimeEdit,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
)

# Thread used to generate the dataset while interface is updated
class Generator(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    canceled = False
    
    def __init__(self, *args, **kwargs):
        super(Generator, self).__init__()
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        print("\014")
        Utils.closeExcel()
        Utils.resetOutputFolder("Output/Generation/")
        #Utils.resetOutputFolder("Output/SubfamiliesActions/")
        Utils.resetOutputFolder("Output/SubfamiliesTransitions/")
        
        Code.Generator.DatasetGenerator.main(self, str(self.args[0]), int(self.args[1]), int(self.args[2]), self.args[3], int(self.args[4]), int(self.args[5]), int(self.args[6]), int(self.args[7]), int(self.args[8]))
        self.finished.emit()
        
# Thread used to generate the dataset while interface is updated
class Statistics(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    canceled = False
    
    def __init__(self, *args, **kwargs):
        super(Statistics, self).__init__()
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        
        mode = ".txt"
        my_file = Path("Output/Generation/Queue_generation.txt")
        if not my_file.is_file():
            mode = ".csv"
        
        if self.args[0] == "statistics":
            queue_path = "Output/Generation/Queue_generation" + mode
            speed_path = "Output/Generation/Speed_generaton" + mode
            Code.Generator.DatasetAnalyser.plotStatistics("queue", queue_path)
            Code.Generator.DatasetAnalyser.plotStatistics("speed", speed_path)
        else:        
            generated_path =  "Output/Generation/trainDataset" + mode
            Code.Generator.DatasetAnalyser.plotData("generated", generated_path)
            Code.Generator.DatasetAnalyser.plotData("real", "realDatasetCleaned.csv")
            #Code.Generator.DatasetAnalyser.plotData("real", "teste.csv")
        
        self.finished.emit()  
        
# Main Window Interface
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dataset Generator")
        self.setWindowIcon(QtGui.QIcon('./Resources/Icons/tkinter_icon.ico'))
        InterfaceUtils.widgetsSetStyle(self, "Styles/style.css")
        
        Configurator.getCountriesFile()
        Configurator.getSuspiciousIPs()
        Configurator.getActionsCheckpoints()
        if Configurator.loadInitConfig("Cybersecurity"):
            print("Cybersecurity configuration file successfully loaded!") 
            
        Configurator.getTicketSazonality()
        InterfaceUtils.setFonts(self)

        self.subwindows = list()
        self.sus_countries = {}
        self.setupMainUi()
    
    # Setups the MainWindow UI
    def setupMainUi(self):
        
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        main_window_layout = QVBoxLayout()
        self.centralWidget.setLayout(main_window_layout)
        
        self.menu_bar = self.menuBar()
        self.menuBarGenerator(self.menu_bar)
        
        self.main_tabwidget = QTabWidget()
        self.main_tabwidget.addTab(self.datasetGenerationTab(),"Dataset Generation")
        self.main_tabwidget.addTab(self.optionsTab(),"Options")
        self.main_tabwidget.addTab(AnalysisWindow.metaAnalysisTab(self), "Meta Analysis")
        
        main_window_layout.addWidget(self.menu_bar)
        #main_window_layout.addWidget(self.editToolBar)
        main_window_layout.addWidget(self.main_tabwidget)
        
    # Sets the menu bar of the UI
    def menuBarGenerator(self, menuBar):
        
        self.help_menu = menuBar.addMenu("&Help")
        self.analysis_menu = menuBar.addMenu("&Analysis")
        
        self.compare_datasets = QAction(self)
        self.compare_datasets.setText("&Real vs Synthetic Dataset")
        self.compare_datasets.triggered.connect(lambda:self.analyseDatasets("plot"))
        #self.compare_generation_modes = QAction(self)
        #self.compare_generation_modes.setText("&Queue vs Speed Generation")
        #self.compare_generation_modes.triggered.connect(lambda:self.analyseDatasets("statistics"))
        
        self.about = QAction(self)
        self.about.setText("&About")
        
        self.analysis_menu.addAction(self.compare_datasets)
        #self.analysis_menu.addAction(self.compare_generation_modes)
        self.help_menu.addAction(self.about)
        
# =============================================================================
#         self.editToolBar = QToolBar()
#         toolButton = QToolButton()
#         toolButton.setText("Compare")
#         toolButton.setCheckable(True)
#         toolButton.setAutoExclusive(True)
#         toolButton.clicked.connect(self.analyseDatasets)
#         self.editToolBar.addWidget(toolButton)
# =============================================================================
     
    # Setups the Options Tab
    def optionsTab(self):
        
        main_layout = QVBoxLayout()
        self.optionsTab = QWidget()
        
        self.loadSelectors(main_layout)
        self.suspiciousCountries(main_layout)
        self.loadOutlierWidgets(main_layout)
        
        self.optionsTab.setLayout(main_layout)
        
        return self.optionsTab
        
    # Setups the Generation Tab
    def datasetGenerationTab(self):
        
        self.generationTab = QWidget()
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        # Ticket
        self.tabs.addTab(self.loadTicketWidgets(self.tabs), "Tickets")
        # Family Generation
        self.tabs.addTab(self.loadFamilyConfigsWidgets(), "Family")
        # Techniques
        self.tabs.addTab(self.loadTechniques(), "Techniques")
        
        #self.tabs.currentChanged.connect(lambda: InterfaceUtils.updateSizes(self, self.tabs.currentIndex()))
        #InterfaceUtils.updateSizes(self, 0)
        
        # Generation Modes
        self.loadGenerationModes()
        # Areas Modes
        self.loadAreas()
        # Debug QCheckBox
        self.loadTeamWidgets()
        # Generate Button
        generate_layout = self.loadGenerateAndProgress()
        
        # Set the layout
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.generation)
        main_layout.addWidget(self.teams_configs)
        main_layout.addWidget(self.areas)
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(generate_layout)
        
        self.generationTab.setLayout(main_layout)
        
        return self.generationTab 
   
    # Setups the IP, Track Behaviours and Outliers of the Options Tab
    def loadSelectors(self, main_layout):
        
        options_params = QHBoxLayout()
        self.ip_label = QLabel("IP:")
        self.ip_toggle = Toggle()
        self.ip_toggle.setChecked(Variables.ip_selector)
        self.ip_toggle.stateChanged.connect(lambda:self.changeIP(self.ip_toggle))
        options_params.addWidget(self.ip_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        options_params.addWidget(self.ip_toggle, alignment=Qt.AlignLeft) 
        
        self.track_behaviour_label = QLabel("Track Behaviours:")
        self.track_behaviour_toggle = Toggle()
        self.track_behaviour_toggle.stateChanged.connect(lambda:self.suspiciousMode(self.track_behaviour_toggle))
        options_params.addWidget(self.track_behaviour_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        options_params.addWidget(self.track_behaviour_toggle, alignment=Qt.AlignLeft) 
        
        self.outlier_label = QLabel("Outliers:")
        self.outlier_toggle = Toggle()
        self.outlier_toggle.setChecked(Variables.outlier_selector)
        self.outlier_toggle.stateChanged.connect(lambda:self.outlierMode(self.outlier_toggle))
        options_params.addWidget(self.outlier_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        options_params.addWidget(self.outlier_toggle, alignment=Qt.AlignLeft) 
        
        main_layout.addLayout(options_params)
        
        ip_layout = QHBoxLayout()  
        self.ip_groupbox = QGroupBox("IP Configurations:", self)
        self.ip_groupbox.setEnabled(Variables.ip_selector)
        self.ip_groupbox.setLayout(ip_layout)
        self.ip_groupbox.setFont(self.features_font)  
        
        self.ip_type = QComboBox()
        self.ip_type.addItems(Variables.ips_pool)
        self.ip_type.currentIndexChanged.connect(self.pickIPaddress)   
        ip_layout.addWidget(self.ip_type, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        main_layout.addWidget(self.ip_groupbox)
    
    # The tracked countries are customized (hour, countries and days off) and loaded according the config file
    def suspiciousCountries(self, main_layout):
        
        self.scroll = QScrollArea()      
        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_content_layout)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_content)
        
        sus_countries_layout = QVBoxLayout() 
        self.sus_countries_groupbox = QGroupBox("Suspicious Countries Configurations:", self) 
        self.sus_countries_groupbox.setLayout(sus_countries_layout)
        self.sus_countries_groupbox.setToolTip("<html><head/><body><p>Choose the generation mode.<ul>  <li>Standard -> uses predefined configurations</li> <li>Custom -> allows a more customized experience</li></p></body></html>")
        self.sus_countries_groupbox.setFont(self.features_font)        
        main_layout.addWidget(self.sus_countries_groupbox)
    
        selectable_countries_layout = QHBoxLayout()
        self.sus_countries_label = QLabel("Countries:")
        self.sus_countries_combo = CheckableComboBox("countries", 0)

        for i in range(len(list(Variables.countries.keys()))):
            self.sus_countries_combo.addItem(list(Variables.countries)[i])
            item = self.sus_countries_combo.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)
            
        self.sus_subfamilies_label = QLabel("Subfamilies:")
        self.sus_subfamilies_spin = QDoubleSpinBox()
        self.sus_subfamilies_spin.setRange(0, 1) 
        self.sus_subfamilies_spin.setSingleStep(0.01)
        self.sus_subfamilies_spin.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.sus_subfamilies_spin.setAlignment(Qt.AlignHCenter) 
        self.sus_subfamilies_spin.setValue(Variables.suspicious_subfamily)
        self.sus_subfamilies_spin.valueChanged.connect(lambda: self.updateCountrySubfamily(self.sus_subfamilies_spin.value()))
         
        selectable_countries_layout.addWidget(self.sus_countries_label, alignment=Qt.AlignLeft | Qt.AlignVCenter) 
        selectable_countries_layout.addWidget(self.sus_countries_combo, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        selectable_countries_layout.addWidget(self.sus_subfamilies_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        selectable_countries_layout.addWidget(self.sus_subfamilies_spin, alignment=Qt.AlignLeft | Qt.AlignVCenter) 
        sus_countries_layout.addLayout(selectable_countries_layout)

        sus_dates_layout = QHBoxLayout()
        #sus_dates_layout.setContentsMargins(0,0,10,0)
        self.sus_dates_widget = QWidget()
        self.sus_dates_widget.setEnabled(False)
        self.sus_dates_widget.setLayout(sus_dates_layout)
        
        self.sus_countries_start_label = QLabel("Start:")
        self.sus_countries_start_time = QTimeEdit(self)
        self.sus_countries_start_time.setTime(QTime(22, 00, 00))
        self.sus_countries_start_time.setObjectName("hourSelector")
        self.sus_countries_start_time.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.sus_countries_start_time.setDisplayFormat('hh:mm:ss')
        
        self.sus_countries_end_label = QLabel("End:")
        self.sus_countries_end_time = QTimeEdit(self)
        self.sus_countries_end_time.setTime(QTime(7, 00, 00))
        self.sus_countries_end_time.setObjectName("hourSelector")
        self.sus_countries_end_time.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.sus_countries_end_time.setDisplayFormat('hh:mm:ss')
        
        sus_dates_layout.addWidget(self.sus_countries_start_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        sus_dates_layout.addWidget(self.sus_countries_start_time, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        sus_dates_layout.addWidget(self.sus_countries_end_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        sus_dates_layout.addWidget(self.sus_countries_end_time, alignment=Qt.AlignHCenter | Qt.AlignVCenter)  
        
        sus_dates_lock_layout = QHBoxLayout()
        #sus_dates_lock_layout.setContentsMargins(0,0,160,0)
        self.sus_countries_lock = QPushButton()
        self.sus_countries_lock.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.sus_countries_lock.setObjectName("country_lock")
        self.sus_countries_lock.setProperty("locked", True)  
        self.sus_countries_lock.pressed.connect(lambda:self.lockDates(self.sus_dates_widget))
        
        sus_dates_lock_layout.addWidget(self.sus_dates_widget, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        sus_dates_lock_layout.addWidget(self.sus_countries_lock, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        sus_countries_layout.addLayout(sus_dates_lock_layout)

        sus_days_off_layout = QHBoxLayout()
        self.sus_days_off_label = QLabel("Days Off:")
        self.sus_days_off_combo = CheckableComboBox("daysoff", 0)
        
        for i in Variables.week_time.keys():
            self.sus_days_off_combo.addItem(Variables.week_time[i]['day'])
            item = self.sus_days_off_combo.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)
            
        self.actions_label = QLabel("Actions:")
        self.actions = QComboBox()
        self.actions.addItem("Select All")
        self.actions.addItem("None")
        self.actions.addItem("Random")
        self.actions.setCurrentIndex(1)
        
        if Variables.suspicious_selector:
            self.addAllSuspiciousCountries(self.sus_countries_combo, self.sus_days_off_combo, self.scroll_content_layout)
        
        self.track_behaviour_toggle.setChecked(Variables.suspicious_selector)
        self.sus_countries_groupbox.setEnabled(Variables.suspicious_selector)
        
        sus_days_off_layout.addWidget(self.actions_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        sus_days_off_layout.addWidget(self.actions, alignment=Qt.AlignLeft | Qt.AlignVCenter) 
        sus_days_off_layout.addWidget(self.sus_days_off_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        sus_days_off_layout.addWidget(self.sus_days_off_combo, alignment=Qt.AlignLeft | Qt.AlignVCenter) 
        
        sus_countries_layout.addLayout(sus_days_off_layout)
        sus_countries_layout.addWidget(self.scroll)

        self.actions.activated.connect(lambda:self.updateCountryDaysOffComboBox(self.actions, self.sus_days_off_combo))  
        self.sus_countries_combo.activated.connect(lambda:self.addSingleSuspiciousCountry(self.sus_countries_combo, self.sus_days_off_combo, self.scroll_content_layout))        

################################ WIDGETS ###############################
    
    # The generation can follow the standard approach (fast) or customized. The debug option is also presented
    def loadGenerationModes(self):        
        
        generation_layout = QHBoxLayout()
        self.generation = QGroupBox("Generation Mode:", self)
        self.generation.setFont(self.features_font)
        
        self.generation_standard = QRadioButton("Standard", self.generation)
        self.generation_standard.setToolTip("<html><head/><body><p>Uses predefined configurations to generate the dataset (Press GENERATE)<ul>  "
                                            "<li> Number of tickets - 1000 </li> "
                                            "<li> Number of families - 24 </li>"
                                            "<li> Number of techniques - 30 </li>"
                                            "<li> Minimum number of subtechniques - 2 </li>"
                                            "<li> Maximum number of subtechniques - 3 </li>"
                                            "</p></body></html>")
        self.generation_standard.setChecked(True)
        self.generation_standard.toggled.connect(self.changeGenerationMode)
        generation_layout.addWidget(self.generation_standard, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        self.generation_custom = QRadioButton("Custom", self)
        self.generation_custom.setToolTip("<html><head/><body><p>The dataset is further tune with new setting. For example, you can change:<ul>  "
                                           "<li> Teams (analysts, and shifts) </li> " 
                                           "<li> Incidents (area and probability) </li> " 
                                           "<li> Tickets (number, and range of dates) </li> "
                                           "<li> Families (number, subfamilies and distribution) </li> "
                                           "<li> Techniques (number) </li>"
                                           "<li> Other options </li>"
                                           "</p></body></html>")
        self.generation_custom.toggled.connect(self.changeGenerationMode)
        generation_layout.addWidget(self.generation_custom, alignment=Qt.AlignHCenter | Qt.AlignVCenter)  
        
        debug_layout = QHBoxLayout()
        self.debug_label = QLabel("Debug:")
        self.debug_toggle = Toggle()
        self.debug_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.debug_toggle.stateChanged.connect(lambda:self.changeDebug(self.debug_toggle))
        debug_layout.addWidget(self.debug_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        debug_layout.addWidget(self.debug_toggle, alignment=Qt.AlignLeft) 
        generation_layout.addLayout(debug_layout)
                
        format_layout = QHBoxLayout()
        self.format_label = QLabel("Format:")
        self.format_options = QComboBox()         
        self.format_options.addItem("CSV")
        self.format_options.addItem("EXCEL")
        
        self.format_options.currentIndexChanged.connect(self.changeFormat)
        format_layout.addWidget(self.format_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        format_layout.addWidget(self.format_options, alignment=Qt.AlignLeft) 
        generation_layout.addLayout(format_layout)
        
        self.generation.setLayout(generation_layout)
    
    # Areas are loaded (cybersecurity, education and other). Furthermore, it opens an new window to customize the incidents
    def loadAreas(self):
        
        area_layout = QHBoxLayout()
        self.areas = QGroupBox("Areas Configurations:", self)
        self.areas.setFont(self.features_font)
        self.areas.setEnabled(False)
        
        domain_layout = QHBoxLayout()
        self.domain_label = QLabel("Area:", self)
        self.domain_options = QComboBox()         
        self.domain_options.setToolTip("<html><head/><body><p>Load the settings of the selected domain. For now, only cybersecurity and education are configured!</p></body></html>")
        self.domain_options.setEditable(True) 
        self.domain_options.setObjectName("domains")
        
        Variables.dataset_field_pool.sort()
        self.addAreas(Variables.dataset_field_pool)
        
        self.domain_options.activated.connect(lambda:self.changeDomain(str(self.domain_options.currentText())))
        domain_layout.addWidget(self.domain_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        domain_layout.addWidget(self.domain_options, alignment=Qt.AlignHCenter | Qt.AlignLeft) 
        area_layout.addLayout(domain_layout)
        
        self.areas_button = QPushButton("Incidents", self) 
        self.areas_button.setToolTip("<html><head/><body><p>Personalize the incidents and their probability of occuring.</p></body></html>")
        self.areas_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.areas_button.clicked.connect(lambda:self.newSubWindow("Areas", str(self.domain_options.currentText())))
        area_layout.addWidget(self.areas_button, alignment=Qt.AlignHCenter | Qt.AlignVCenter)  

        self.areas.setLayout(area_layout)
    
    # Customize the analysts of each team
    def loadTeamWidgets(self):
        
        team_configs_layout = QHBoxLayout()
        self.teams_configs = QGroupBox("Team Configurations:", self)
        self.teams_configs.setLayout(team_configs_layout)
        self.teams_configs.setFont(self.features_font)
        self.teams_configs.setEnabled(False)
        
        subfamily_prob_layout = QHBoxLayout()
        self.analyst_subfamily_label = QLabel("Subfamily Probability:")
        self.analyst_subfamily_spin = QDoubleSpinBox()
        self.analyst_subfamily_spin.setRange(0, 1) 
        self.analyst_subfamily_spin.setSingleStep(0.01)
        self.analyst_subfamily_spin.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.analyst_subfamily_spin.setAlignment(Qt.AlignHCenter) 
        self.analyst_subfamily_spin.setValue(Variables.analyst_subfamily_action_probability)
        self.analyst_subfamily_spin.valueChanged.connect(lambda: self.updateAnalystProbSubfamily(self.analyst_subfamily_spin.value()))
        subfamily_prob_layout.addWidget(self.analyst_subfamily_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        subfamily_prob_layout.addWidget(self.analyst_subfamily_spin, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
            
        same_analyst_action_layout = QHBoxLayout()
        self.same_analyst_action_label = QLabel("Same action Probability:")
        self.same_analyst_action_spin = QDoubleSpinBox()
        self.same_analyst_action_spin.setRange(0, 1) 
        self.same_analyst_action_spin.setSingleStep(0.01)
        self.same_analyst_action_spin.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.same_analyst_action_spin.setAlignment(Qt.AlignHCenter) 
        self.same_analyst_action_spin.setValue(Variables.analyst_same_action_probability)
        self.same_analyst_action_spin.valueChanged.connect(lambda: self.updateSameAnalystAction(self.same_analyst_action_spin.value()))
        same_analyst_action_layout.addWidget(self.same_analyst_action_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        same_analyst_action_layout.addWidget(self.same_analyst_action_spin, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        # Team Allocation Type QCheckBox
        self.users_settings = QCheckBox("New Users Settings")
        self.users_settings.setChecked(Variables.reset_user_shift_daysoff)
        self.users_settings.setLayoutDirection(Qt.RightToLeft) 
        self.users_settings.stateChanged.connect(lambda:self.changeUserInfo(self.users_settings))
        
        action_layout = QVBoxLayout()
        action_layout.addLayout(subfamily_prob_layout) 
        action_layout.addLayout(same_analyst_action_layout)
        action_layout.addWidget(self.users_settings, alignment=Qt.AlignHCenter | Qt.AlignRight)
        
        # Analysts Window
        self.analysts_button = QPushButton("Analysts", self) 
        self.debug_toggle.setToolTip("<html><head/><body><p>Customize the the analysts of each team and their shifts</p></body></html>")
        self.analysts_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.analysts_button.clicked.connect(lambda:self.newSubWindow("Analysts", str(self.domain_options.currentText())))
        
        team_configs_layout.addLayout(action_layout) 
        team_configs_layout.addWidget(self.analysts_button,alignment=Qt.AlignHCenter | Qt.AlignVCenter)
    
    # Customize the ticket generations (number, start date and end date)
    def loadTicketWidgets(self, parent):
        
        self.ticketTab = QWidget()
        self.ticketTab.setEnabled(False)

        date_layout = QVBoxLayout()
        date_layout.setSpacing(10)

        train_ticket_number_layout = QHBoxLayout()
        self.train_ticket = QLabel("Number:", self)
        self.ticket_train_number = QLineEdit()
        self.ticket_train_number.setText(str(Variables.standard_params['parameters']['train_ticket']))
        self.ticket_train_number.setObjectName("ticket_train")
        self.ticket_train_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        ticketValidator = QtGui.QIntValidator(1, 10000000)
        self.ticket_train_number.setValidator(ticketValidator)
        self.ticket_train_number.setFont(self.features_font)
        self.ticket_train_number.textChanged.connect(lambda:self.checkInput(self.ticket_train_number))
        train_ticket_number_layout.addWidget(self.train_ticket, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        train_ticket_number_layout.addWidget(self.ticket_train_number, alignment = Qt.AlignLeft)
         
        date_layout_init = QHBoxLayout()
        self.date_init = QLabel("Initial:", self)
        
        self.date_init_input = QDateTimeEdit()
        self.date_init_input.setDisplayFormat("dd-MM-yyyy HH:mm:ss")
        self.date_init_input.setFont(self.features_font)
        self.date_init_input.setDateTime(datetime.strptime(Variables.start_date, '%d-%m-%Y %H:%M:%S'))
        self.date_init_input.dateTimeChanged.connect(lambda: self.updateTicketDates("initial datetime")) 
        self.date_init_input.setCalendarPopup(True)
        
        date_layout.addLayout(train_ticket_number_layout)
        date_layout_init.addWidget(self.date_init, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        date_layout_init.addWidget(self.date_init_input, alignment = Qt.AlignLeft)
        date_layout.addLayout(date_layout_init)
        
        date_layout_end = QHBoxLayout()
        self.date_end = QLabel("End:", self)
        self.date_end_input = QDateTimeEdit(parent)
        self.date_end_input.setFont(self.features_font)
        self.date_end_input.setDisplayFormat("d-M-yyyy HH:mm:ss")
        self.date_end_input.setDateTime(datetime.strptime(Variables.end_date, '%d-%m-%Y %H:%M:%S'))
        self.date_end_input.dateTimeChanged.connect(lambda: self.updateTicketDates("end datetime")) 
        self.date_end_input.setCalendarPopup(True)
        date_layout_end.addWidget(self.date_end, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        date_layout_end.addWidget(self.date_end_input, alignment = Qt.AlignLeft)   
        date_layout.addLayout(date_layout_end)
        
        escalation_widget = QWidget()
        escalation_layout = QHBoxLayout()
        escalation_widget.setLayout(escalation_layout)
        
        self.escalate_label = QLabel("Escalation Probability:", self)
        escalation_layout.addWidget(self.escalate_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        escalation_layout_content = QHBoxLayout()
        escalation_layout_content.setContentsMargins(34, 0, 0, 0)
        self.escalation_slider = QSlider(Qt.Horizontal)
        self.escalation_slider.setFixedWidth(160)
        self.escalation_slider.setMinimum(1)
        self.escalation_slider.setMaximum(5)
        self.escalation_slider.setValue(Variables.escalate_rate_percentage)
        self.escalation_slider.setTickPosition(QSlider.TicksBelow)
        self.escalation_slider.setTickInterval(1)
        self.escalation_slider.sliderReleased.connect(lambda: self.updateEscalateRate(self.escalation_slider.value()))
        self.escalation_rate_label = QLabel("Rate: " + str(self.escalation_slider.value()) + "%", self)
        
        ticket_season_layout = QHBoxLayout()
        ticket_season_layout.setContentsMargins(18, 0, 0, 0)
        self.ticket_season_label = QLabel("Ticket Seasonality:")
        self.ticket_season_toggle = Toggle()
        self.ticket_season_toggle.setChecked(Variables.ticket_seasonality_selector)
        self.ticket_season_toggle.stateChanged.connect(lambda:self.changeTicketSeasonality(self.ticket_season_toggle))
        ticket_season_layout.addWidget(self.ticket_season_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        ticket_season_layout.addWidget(self.ticket_season_toggle, alignment=Qt.AlignLeft) 
        
        escalation_layout_content.addWidget(self.escalation_slider)
        escalation_layout_content.addWidget(self.escalation_rate_label)
        escalation_layout.addLayout(escalation_layout_content)
        
        date_layout.addWidget(escalation_widget, alignment = Qt.AlignHCenter | Qt.AlignTop)
        date_layout.addLayout(ticket_season_layout)
        self.ticketTab.setLayout(date_layout)
        
        return self.ticketTab 
    
    # Customize the families (default, number of families, minimum number of subfamilies, maximum number of subfamilies and distribution according to the time of day and weekday)
    def loadFamilyConfigsWidgets(self):
        
        self.familyTab = QWidget()
        self.familyTab.setEnabled(False)        
        family_default_layout = QVBoxLayout()
        
        self.family_scroll = QScrollArea()
        self.family_scroll.setWidgetResizable(True)
        self.family_scroll.setWidget(self.familyTab)

        default_layout = QHBoxLayout() 
        self.family_default_checkbox = QRadioButton("Default")
        #default_layout.setContentsMargins(0,0,30,0)
        self.family_default_checkbox.setChecked(True)
        self.family_default_checkbox.setLayoutDirection(Qt.RightToLeft) 
        self.family_default_checkbox.toggled.connect(lambda:self.familyDefaultMode(self.family_default_checkbox))
        default_layout.addWidget(self.family_default_checkbox, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
# =============================================================================
#         self.subfamily_coordinated_checkbox = QRadioButton("Multiple Attack Detection")
#         self.subfamily_coordinated_checkbox.setChecked(True)
#         self.subfamily_coordinated_checkbox.setLayoutDirection(Qt.RightToLeft) 
#         self.subfamily_coordinated_checkbox.toggled.connect(self.multipleAttackMode)
#         default_layout.addWidget(self.subfamily_coordinated_checkbox, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
# =============================================================================
        
        plot_layout = QHBoxLayout()
        self.plot_label = QLabel("Plots:")
        self.plot_toggle = Toggle()
        self.plot_toggle.setToolTip("<html><head/><body><p>Used for debugging</p></body></html>")
        self.plot_toggle.stateChanged.connect(lambda:self.printPlots(self.plot_toggle))
        plot_layout.addWidget(self.plot_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        plot_layout.addWidget(self.plot_toggle, alignment=Qt.AlignLeft) 
        
        family_season_layout = QHBoxLayout()
        self.family_season_label = QLabel("Family Seasonality:")
        self.family_season_toggle = Toggle()
        self.family_season_toggle.setChecked(Variables.family_seasonality_selector)
        self.family_season_toggle.stateChanged.connect(lambda:self.changeFamilySeasonality(self.family_season_toggle))
        family_season_layout.addWidget(self.family_season_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        family_season_layout.addWidget(self.family_season_toggle, alignment=Qt.AlignLeft) 
        
        default_layout.addLayout(plot_layout)
        default_layout.addLayout(family_season_layout)
        family_default_layout.addLayout(default_layout)
        
        family_layout = QHBoxLayout() 
        self.family_label = QLabel("Number of Families:", self)
        self.family_number = QLineEdit()
        self.family_number.setText(str(Variables.standard_params['parameters']['families_number']))
        self.family_number.setObjectName("family_number")
        self.family_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.family_number.textChanged.connect(lambda:self.checkInput(self.family_number))
        familyValidator = QtGui.QIntValidator(1, 24)
        self.family_number.setValidator(familyValidator)
        self.family_number.setFont(self.features_font)
        family_layout.addWidget(self.family_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        family_layout.addWidget(self.family_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        family_default_layout.addLayout(family_layout)
        
        min_sub_family_layout = QHBoxLayout() 
        #min_sub_family_layout.setContentsMargins(5,0,180,0)
        self.min_subfamily_label = QLabel("Minimum Number of SubFamilies:", self)
        self.min_subfamily_number = QLineEdit()
        self.min_subfamily_number.setText(str(Variables.standard_params['parameters']['minsubfamilies_number']))
        self.min_subfamily_number.setObjectName("minimum_subFamilies")
        self.min_subfamily_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.min_subfamily_number.textChanged.connect(lambda:self.checkInput(self.min_subfamily_number))
        minsubfamilyValidator = QtGui.QIntValidator(1, 4)
        self.min_subfamily_number.setValidator(minsubfamilyValidator)
        self.min_subfamily_number.setFont(self.features_font)
        min_sub_family_layout.addWidget(self.min_subfamily_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_sub_family_layout.addWidget(self.min_subfamily_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        family_default_layout.addLayout(min_sub_family_layout)
        
        max_sub_family_layout = QHBoxLayout() 
        #max_sub_family_layout.setContentsMargins(5,0,180,0)
        self.max_subfamily_label = QLabel("Maximum Number of SubFamilies:", self)
        self.max_subfamily_number = QLineEdit()
        self.max_subfamily_number.setText(str(Variables.standard_params['parameters']['maxsubfamilies_number']))
        self.max_subfamily_number.setObjectName("maximum_subFamilies")
        self.max_subfamily_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.max_subfamily_number.textChanged.connect(lambda:self.checkInput(self.max_subfamily_number))
        maxsubfamilyValidator = QtGui.QIntValidator(5, 8)
        self.max_subfamily_number.setValidator(maxsubfamilyValidator)
        self.max_subfamily_number.setFont(self.features_font)
        max_sub_family_layout.addWidget(self.max_subfamily_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_sub_family_layout.addWidget(self.max_subfamily_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        family_default_layout.addLayout(max_sub_family_layout)
        
        selectable_families_layout = QHBoxLayout()
        self.selectable_families_label = QLabel("Types of Families:")
        self.selectable_families_combo = CheckableComboBox("families", int(self.family_number.text()))
        self.selectable_families_combo.setEnabled(False)

        for i in range(len(string.ascii_uppercase)):
            self.selectable_families_combo.addItem(string.ascii_uppercase[i])
            item = self.selectable_families_combo.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)
            
        selectable_families_layout.addWidget(self.selectable_families_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        selectable_families_layout.addWidget(self.selectable_families_combo, alignment=Qt.AlignLeft | Qt.AlignVCenter)
         
        family_default_layout.addLayout(selectable_families_layout)
        
        selected_families_layout = QHBoxLayout()
        self.selected_families_label = QLabel("Selected Families:")
        self.selected_families = QLabel("Random")
        selected_families_layout.addWidget(self.selected_families_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        selected_families_layout.addWidget(self.selected_families, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        family_default_layout.addLayout(selected_families_layout)
        
        self.selectable_families_combo.activated.connect(lambda:self.addFamily(self.selectable_families_combo, self.selected_families))   
        
        self.coordinated_attacks_groupbox = QGroupBox("Coordinated Attack:", self)
        self.coordinated_attacks_groupbox.setEnabled(True)
        coordinated_layout = QVBoxLayout()
        self.coordinated_attacks_groupbox.setLayout(coordinated_layout)       

        min_occurences_layout = QHBoxLayout() 
        self.min_occurences_label = QLabel("Minimum Number of Occurences:", self)
        self.min_occurences_number = QLineEdit()
        self.min_occurences_number.setText(str(Variables.min_coordinated_attack))
        self.min_occurences_number.setObjectName("minimum_attack_occurences")
        self.min_occurences_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.min_occurences_number.textChanged.connect(lambda:self.checkInput(self.min_occurences_number))
        minsubfamilyValidator = QtGui.QIntValidator(1, 4)
        self.min_occurences_number.setValidator(minsubfamilyValidator)
        self.min_occurences_number.setFont(self.features_font)
        min_occurences_layout.addWidget(self.min_occurences_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_occurences_layout.addWidget(self.min_occurences_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        coordinated_layout.addLayout(min_occurences_layout)
        
        max_occurences_layout = QHBoxLayout() 
        self.max_occurences_label = QLabel("Maximum Number of Occurences:", self)
        self.max_occurences_number = QLineEdit()
        self.max_occurences_number.setText(str(Variables.max_coordinated_attack))
        self.max_occurences_number.setObjectName("maximum_attack_occurences")
        self.max_occurences_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.max_occurences_number.textChanged.connect(lambda:self.checkInput(self.max_occurences_number))
        minsubfamilyValidator = QtGui.QIntValidator(2, 4)
        self.max_occurences_number.setValidator(minsubfamilyValidator)
        self.min_occurences_number.setFont(self.features_font)
        max_occurences_layout.addWidget(self.max_occurences_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_occurences_layout.addWidget(self.max_occurences_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        coordinated_layout.addLayout(max_occurences_layout)
        
        min_attack_timerange_layout = QHBoxLayout()
        self.min_attack_timerange_label = QLabel("Minimum range time detection:", self)
        min_attack_timerange_layout.addWidget(self.min_attack_timerange_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        min_attack_timerange_slider_layout = QHBoxLayout()
        #temp_layout.setContentsMargins(20, 0, 0, 0)
        self.min_attack_timerange_slider = QSlider(Qt.Horizontal)
        self.min_attack_timerange_slider.setFixedWidth(200)
        self.min_attack_timerange_slider.setMinimum(20)
        self.min_attack_timerange_slider.setMaximum(59)
        self.min_attack_timerange_slider.setValue(Variables.min_coordinated_attack_minutes)
        self.min_attack_timerange_slider.setTickPosition(QSlider.TicksBelow)
        self.min_attack_timerange_slider.setTickInterval(1)
        
        self.min_attack_timerange_rate_label = QLabel(str(self.min_attack_timerange_slider.value()) + " minutes", self)        
        self.min_attack_timerange_rate_label.setObjectName('min_time_detection')
        
        min_attack_timerange_slider_layout.addWidget(self.min_attack_timerange_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_attack_timerange_slider_layout.addWidget(self.min_attack_timerange_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_attack_timerange_layout.addLayout(min_attack_timerange_slider_layout)
        coordinated_layout.addLayout(min_attack_timerange_layout)
        
        max_attack_timerange_layout = QHBoxLayout()
        self.max_attack_timerange_label = QLabel("Maximum range time detection:", self)
        max_attack_timerange_layout.addWidget(self.max_attack_timerange_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        max_attack_timerange_slider_layout = QHBoxLayout()
        #temp_layout.setContentsMargins(20, 0, 0, 0)
        self.max_attack_timerange_slider = QSlider(Qt.Horizontal)
        self.max_attack_timerange_slider.setFixedWidth(200)
        self.max_attack_timerange_slider.setMinimum(60)
        self.max_attack_timerange_slider.setMaximum(120)
        self.max_attack_timerange_slider.setValue(Variables.max_coordinated_attack_minutes)
        self.max_attack_timerange_slider.setTickPosition(QSlider.TicksBelow)
        self.max_attack_timerange_slider.setTickInterval(1)
        
        self.max_attack_timerange_rate_label = QLabel(str(self.max_attack_timerange_slider.value()) + " minutes", self)        
        self.max_attack_timerange_rate_label.setObjectName('max_time_detection')
        
        max_attack_timerange_slider_layout.addWidget(self.max_attack_timerange_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_attack_timerange_slider_layout.addWidget(self.max_attack_timerange_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_attack_timerange_layout.addLayout(max_attack_timerange_slider_layout)
        coordinated_layout.addLayout(max_attack_timerange_layout)
        
        self.min_attack_timerange_slider.sliderReleased.connect(lambda: self.updateDetectionTimeRange(self.min_attack_timerange_slider, self.min_attack_timerange_rate_label))
        self.max_attack_timerange_slider.sliderReleased.connect(lambda: self.updateDetectionTimeRange(self.max_attack_timerange_slider, self.max_attack_timerange_rate_label))
        
        self.distribution_groupbox = QGroupBox("Distribution:", self)
        self.distribution_groupbox.setEnabled(False)
        distribution_layout = QHBoxLayout()
        self.distribution_groupbox.setLayout(distribution_layout)       
        
        self.family_distribution_normal = QRadioButton("Normal")
        self.family_distribution_normal.setChecked(True)
        self.family_distribution_normal.setLayoutDirection(Qt.RightToLeft) 
        self.family_distribution_normal.toggled.connect(lambda:self.distributionMode(self.family_distribution_normal))
        
        self.family_distribution_uniform = QRadioButton("Uniform")
        self.family_distribution_uniform.setLayoutDirection(Qt.RightToLeft) 
        self.family_distribution_uniform.toggled.connect(lambda:self.distributionMode(self.family_distribution_uniform))
        
        distribution_layout.addWidget(self.family_distribution_normal, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        distribution_layout.addWidget(self.family_distribution_uniform, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        family_default_layout.addWidget(self.distribution_groupbox)
       
        family_grid = QGridLayout()
        self.time_generation = QGroupBox("Time Probabilities:", self)
        self.time_generation.setEnabled(False)
        self.time_layout = QVBoxLayout()
        self.time_generation.setLayout(self.time_layout)       
        
        self.time_equal = QRadioButton("Equal in all hours")
        self.time_equal.setChecked(True)
        self.time_equal.setLayoutDirection(Qt.RightToLeft) 
        self.time_equal.toggled.connect(lambda:self.timeMode(self.time_equal))
        self.time_layout.addWidget(self.time_equal, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        self.time_day_light = QLabel("Higher on Daylight", self)
        self.time_day_light_layout = QHBoxLayout()
        self.spin_time_day_light = QDoubleSpinBox()
        self.spin_time_day_light.setAlignment(Qt.AlignCenter)
        self.spin_time_day_light.setEnabled(False)
        self.spin_time_day_light.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.spin_time_day_light.setRange(0, 1)
        self.spin_time_day_light.setValue(Variables.family_time_4h[2]['prob'] + Variables.family_time_4h[3]['prob'] + Variables.family_time_4h[4]['prob'])
        self.spin_time_day_light.setSingleStep(0.01)
        self.spin_time_day_light.valueChanged.connect(lambda:self.updateTimeFamiliesProbs(self.time_day_light, self.spin_time_day_light))
        self.time_day_light_layout.addWidget(self.time_day_light)
        self.time_day_light_layout.addWidget(self.spin_time_day_light)
        
        self.time_night_light = QLabel("Higher on Night", self)
        self.time_night_light_layout = QHBoxLayout()
        self.spin_time_night_light = QDoubleSpinBox()
        self.spin_time_night_light.setAlignment(Qt.AlignCenter)
        self.spin_time_night_light.setEnabled(False)
        self.spin_time_night_light.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.spin_time_night_light.setRange(0, 1)
        self.spin_time_night_light.setValue(Variables.family_time_4h[0]['prob'] + Variables.family_time_4h[1]['prob'] + Variables.family_time_4h[5]['prob'])
        self.spin_time_night_light.setSingleStep(0.01)
        self.spin_time_night_light.valueChanged.connect(lambda:self.updateTimeFamiliesProbs(self.time_night_light, self.spin_time_night_light))
        self.time_night_light_layout.addWidget(self.time_night_light)
        self.time_night_light_layout.addWidget(self.spin_time_night_light)
 
        self.time_layout.addLayout(self.time_day_light_layout)
        self.time_layout.addLayout(self.time_night_light_layout)
        family_grid.addWidget(self.time_generation, 0, 0)
        
        # Week
        self.week_generation = QGroupBox("Week Probabilities:", self)
        self.week_generation.setEnabled(False)
        self.week_family_layout = QVBoxLayout()
        self.week_generation.setLayout(self.week_family_layout)  
         
        self.week_equal = QRadioButton("Equal in all days")
        self.week_equal.setChecked(True)
        self.week_equal.setLayoutDirection(Qt.RightToLeft) 
        self.week_equal.toggled.connect(lambda:self.weekMode(self.week_equal))
        self.week_family_layout.addWidget(self.week_equal, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        self.week_label = QLabel("Higher on Weekdays", self)
        self.week_layout = QHBoxLayout()
        self.spin_week = QDoubleSpinBox()
        self.spin_week.setAlignment(Qt.AlignCenter)
        self.spin_week.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.spin_week.setEnabled(False)
        self.spin_week.setRange(0, 1)
        self.spin_week.setValue(Variables.week_time[0]['prob'] + Variables.week_time[1]['prob'] + Variables.week_time[2]['prob'] + Variables.week_time[3]['prob'] + Variables.week_time[4]['prob'])
        self.spin_week.setSingleStep(0.01)
        self.spin_week.valueChanged.connect(lambda:self.updateWeekFamiliesProbs(self.week_label, self.spin_week))
        self.week_layout.addWidget(self.week_label)
        self.week_layout.addWidget(self.spin_week)
        
        self.weekend_label = QLabel("Higher on Weekend", self)
        self.weekend_layout = QHBoxLayout()
        self.spin_weekend = QDoubleSpinBox()
        self.spin_weekend.setEnabled(False)
        self.spin_weekend.setAlignment(Qt.AlignCenter)
        self.spin_weekend.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.spin_weekend.setRange(0, 1)
        self.spin_weekend.setValue(Variables.week_time[5]['prob'] + Variables.week_time[6]['prob'])
        self.spin_weekend.setSingleStep(0.01)
        self.spin_weekend.valueChanged.connect(lambda:self.updateWeekFamiliesProbs(self.weekend_label, self.spin_weekend))
        self.weekend_layout.addWidget(self.weekend_label)
        self.weekend_layout.addWidget(self.spin_weekend)
        
        self.week_family_layout.addLayout(self.week_layout)
        self.week_family_layout.addLayout(self.weekend_layout)   
        family_grid.addWidget(self.week_generation, 0, 1)
        family_default_layout.addLayout(family_grid)
        
        family_default_layout.addWidget(self.coordinated_attacks_groupbox)
        self.familyTab.setLayout(family_default_layout)
        
        return self.family_scroll
    
    # Customizes the techniques (number, minimum subtechniques, maximum subtechniques)
    def loadTechniques(self):
        
        self.techniquesTab = QWidget()
        self.techniquesTab.setEnabled(False)
        
        self.techniques_scroll = QScrollArea()
        self.techniques_scroll.setWidgetResizable(True)
        self.techniques_scroll.setWidget(self.techniquesTab)
        techniques_configs_layout = QVBoxLayout()
        
        technique_layout = QHBoxLayout()  
        self.technique_label = QLabel("Number:", self)
        self.technique_number = QLineEdit()
        self.technique_number.setText(str(Variables.standard_params['parameters']['techniques_number']))
        self.technique_number.setObjectName("techniques_number")
        self.technique_number.textChanged.connect(lambda:self.checkInput(self.technique_number))
        self.technique_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        techniqueValidator = QtGui.QIntValidator(1, 62)
        self.technique_number.setValidator(techniqueValidator)
        self.technique_number.setFont(self.features_font)
        technique_layout.addWidget(self.technique_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        technique_layout.addWidget(self.technique_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        # Min subTechniques
        min_subtechnique_layout = QHBoxLayout()
        self.min_subtechnique_label = QLabel("Sub techniques minimum:", self)
        self.min_subtechnique_number = QLineEdit() 
        self.min_subtechnique_number.setText(str(Variables.standard_params['parameters']['minsubtechniques_number']))
        self.min_subtechnique_number.setEnabled(False)
        self.min_subtechnique_number.setObjectName("min_subtechnique")
        self.min_subtechnique_number.textChanged.connect(lambda:self.checkInput(self.min_subtechnique_number))
        self.min_subtechnique_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.min_subtechnique_number.setValidator(QtGui.QIntValidator())
        self.min_subtechnique_number.setFont(self.features_font)
        min_subtechnique_layout.addWidget(self.min_subtechnique_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_subtechnique_layout.addWidget(self.min_subtechnique_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        #min_subtechnique_widget = QWidget()
        min_subtechniques_dur_layout = QHBoxLayout()
        #min_subtechnique_widget.setLayout(min_subtechniques_dur_layout)
        
        self.min_subtechniques_dur_label = QLabel("Sub techniques minimum rate:", self)
        min_subtechniques_dur_layout.addWidget(self.min_subtechniques_dur_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        temp_layout = QHBoxLayout()
        #temp_layout.setContentsMargins(20, 0, 0, 0)
        self.min_subtechnique_slider = QSlider(Qt.Horizontal)
        self.min_subtechnique_slider.setFixedWidth(200)
        self.min_subtechnique_slider.setMinimum(50)
        self.min_subtechnique_slider.setMaximum(199)
        self.min_subtechnique_slider.setValue(Variables.min_subtechnique_rate)
        self.min_subtechnique_slider.setTickPosition(QSlider.TicksBelow)
        self.min_subtechnique_slider.setTickInterval(1)
        
        self.min_subtechniques_dur_rate_label = QLabel("Rate: " + str(self.min_subtechnique_slider.value()) + "%", self)        
        self.min_subtechniques_dur_rate_label.setObjectName('min_sub')
        
        temp_layout.addWidget(self.min_subtechnique_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        temp_layout.addWidget(self.min_subtechniques_dur_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_subtechniques_dur_layout.addLayout(temp_layout)
        
        #min_subtechnique_cost_widget = QWidget()
        min_subtechniques_cost_layout = QHBoxLayout()
        #min_subtechnique_cost_widget.setLayout(min_subtechniques_cost_layout)
        
        self.min_subtechniques_cost_label = QLabel("Sub techniques minimum cost:", self)
        min_subtechniques_cost_layout.addWidget(self.min_subtechniques_cost_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        temp_layout = QHBoxLayout()
        #temp_layout.setContentsMargins(20, 0, 0, 0)
        self.min_subtechnique_cost_slider = QSlider(Qt.Horizontal)
        self.min_subtechnique_cost_slider.setFixedWidth(200)
        self.min_subtechnique_cost_slider.setMinimum(1)
        self.min_subtechnique_cost_slider.setMaximum(5)
        self.min_subtechnique_cost_slider.setValue(Variables.min_subtechnique_cost)
        self.min_subtechnique_cost_slider.setTickPosition(QSlider.TicksBelow)
        self.min_subtechnique_cost_slider.setTickInterval(1)
        
        self.min_subtechniques_cost_rate_label = QLabel("Cost: " + str(self.min_subtechnique_cost_slider.value()), self)        
        self.min_subtechniques_cost_rate_label.setObjectName('min_sub_cost')
        
        temp_layout.addWidget(self.min_subtechnique_cost_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        temp_layout.addWidget(self.min_subtechniques_cost_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        min_subtechniques_cost_layout.addLayout(temp_layout)
        
        # Max subTechniques
        max_subtechnique_layout = QHBoxLayout()
        self.max_subtechnique_label = QLabel("Sub techniques maximum:", self)
        self.max_subtechnique_number = QLineEdit()
        self.max_subtechnique_number.setText(str(Variables.standard_params['parameters']['maxsubtechniques_number']))
        self.max_subtechnique_number.setEnabled(False)
        self.max_subtechnique_number.setObjectName("max_subtechnique")
        self.max_subtechnique_number.textChanged.connect(lambda:self.checkInput(self.max_subtechnique_number))
        self.max_subtechnique_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.max_subtechnique_number.setValidator(QtGui.QIntValidator())
        self.max_subtechnique_number.setFont(self.features_font)
        max_subtechnique_layout.addWidget(self.max_subtechnique_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_subtechnique_layout.addWidget(self.max_subtechnique_number, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        #max_subtechnique_cost_widget = QWidget()
        max_subtechniques_cost_layout = QHBoxLayout()
        #max_subtechnique_cost_widget.setLayout(max_subtechniques_cost_layout)
        
        self.max_subtechniques_cost_label = QLabel("Sub techniques maximum cost:", self)
        max_subtechniques_cost_layout.addWidget(self.max_subtechniques_cost_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        temp_layout = QHBoxLayout()
        self.max_subtechnique_cost_slider = QSlider(Qt.Horizontal)
        self.max_subtechnique_cost_slider.setFixedWidth(200)
        self.max_subtechnique_cost_slider.setMinimum(6)
        self.max_subtechnique_cost_slider.setMaximum(9)
        self.max_subtechnique_cost_slider.setValue(Variables.max_subtechnique_cost)
        self.max_subtechnique_cost_slider.setTickPosition(QSlider.TicksBelow)
        self.max_subtechnique_cost_slider.setTickInterval(1)
        
        self.max_subtechniques_cost_rate_label = QLabel("Cost: " + str(self.max_subtechnique_cost_slider.value()), self)
        self.max_subtechniques_cost_rate_label.setObjectName('max_sub_cost')
        
        self.min_subtechnique_cost_slider.sliderReleased.connect(lambda: self.updateSubTechniqueCost(self.min_subtechnique_cost_slider, self.min_subtechniques_cost_rate_label))
        self.max_subtechnique_cost_slider.sliderReleased.connect(lambda: self.updateSubTechniqueCost(self.max_subtechnique_cost_slider, self.max_subtechniques_cost_rate_label))
        
        temp_layout.addWidget(self.max_subtechnique_cost_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        temp_layout.addWidget(self.max_subtechniques_cost_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_subtechniques_cost_layout.addLayout(temp_layout)
        
        #max_subtechnique_widget = QWidget()
        max_subtechniques_dur_layout = QHBoxLayout()
        #max_subtechnique_widget.setLayout(max_subtechniques_dur_layout)
        
        self.max_subtechniques_dur_label = QLabel("Sub techniques maximum rate:", self)
        max_subtechniques_dur_layout.addWidget(self.max_subtechniques_dur_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        temp_layout = QHBoxLayout()
        #temp_layout.setContentsMargins(100, 0, 0, 0)
        self.max_subtechnique_slider = QSlider(Qt.Horizontal)
        self.max_subtechnique_slider.setFixedWidth(200)
        self.max_subtechnique_slider.setMinimum(51)
        self.max_subtechnique_slider.setMaximum(200)
        self.max_subtechnique_slider.setValue(Variables.max_subtechnique_rate)
        self.max_subtechnique_slider.setTickPosition(QSlider.TicksBelow)
        self.max_subtechnique_slider.setTickInterval(1)
        
        self.max_subtechniques_dur_rate_label = QLabel("Rate: " + str(self.max_subtechnique_slider.value()) + "%", self)
        self.max_subtechniques_dur_rate_label.setObjectName('max_sub')
        
        self.min_subtechnique_slider.sliderReleased.connect(lambda: self.updateSubTechniqueRate(self.min_subtechnique_slider, self.min_subtechniques_dur_rate_label))
        self.max_subtechnique_slider.sliderReleased.connect(lambda: self.updateSubTechniqueRate(self.max_subtechnique_slider, self.max_subtechniques_dur_rate_label))
        
        temp_layout.addWidget(self.max_subtechnique_slider, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        temp_layout.addWidget(self.max_subtechniques_dur_rate_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        max_subtechniques_dur_layout.addLayout(temp_layout)
        
        techniques_configs_layout.addLayout(technique_layout)
        techniques_configs_layout.addLayout(min_subtechnique_layout)
        techniques_configs_layout.addLayout(min_subtechniques_cost_layout)
        techniques_configs_layout.addLayout(min_subtechniques_dur_layout)
        
        techniques_configs_layout.addLayout(max_subtechnique_layout)
        techniques_configs_layout.addLayout(max_subtechniques_cost_layout)
        techniques_configs_layout.addLayout(max_subtechniques_dur_layout)
       
        self.techniquesTab.setLayout(techniques_configs_layout)
        
        return self.techniques_scroll
    
    # Customize the outlier (impact and frequency)
    def loadOutlierWidgets(self, main_layout):
        
        outlier_layout = QHBoxLayout()
        self.outlier_groupbox = QGroupBox("Outlier Configurations:", self)
        self.outlier_groupbox.setEnabled(Variables.outlier_selector)
        self.outlier_groupbox.setLayout(outlier_layout)

        self.outlier = QLabel("Extra Action Cost:", self)
        self.outlier.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        outlier_layout.addWidget(self.outlier)
        
        self.outlier_spin = QDoubleSpinBox()
        self.outlier_spin.setRange(0, 1) 
        self.outlier_spin.setSingleStep(0.01)
        self.outlier_spin.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.outlier_spin.setAlignment(Qt.AlignHCenter) 
        self.outlier_spin.setValue(Variables.outlier_cost)
        self.outlier_spin.valueChanged.connect(lambda: self.updateOutlierValue(self.outlier_spin.value()))
        outlier_layout.addWidget(self.outlier_spin, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
         
        outlier_rate = QVBoxLayout()
        outlier_rate.setContentsMargins(0, 25, 0, 0)
        self.outlier_slider = QSlider(Qt.Horizontal)
        self.outlier_slider.setFixedWidth(200)
        self.outlier_slider.setMinimum(1)
        self.outlier_slider.setMaximum(20)
        self.outlier_slider.setValue(10)
        self.outlier_slider.setTickPosition(QSlider.TicksBelow)
        self.outlier_slider.setTickInterval(1)
        self.outlier_slider.sliderReleased.connect(lambda: self.updateOutlierRate(self.outlier_slider.value()))
        
        self.outlier_rate_output = QLabel("Frequency rate:" + str(Variables.outlier_rate) + "%", self)
        self.outlier_rate_output.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.outlier_rate_output.setFont(self.features_font)
       
        outlier_rate.addWidget(self.outlier_slider, alignment = Qt.AlignHCenter | Qt.AlignBottom)
        outlier_rate.addWidget(self.outlier_rate_output, alignment = Qt.AlignHCenter | Qt.AlignTop)
        outlier_layout.addLayout(outlier_rate)
        
        main_layout.addWidget(self.outlier_groupbox)
    
    # Sets the generate button and generation status
    def loadGenerateAndProgress(self):
              
        bar_layout = QVBoxLayout()
        self.generate_button = QPushButton("Generate",self) 
        self.generate_button.setObjectName('generateButton')
        self.generate_button.setProperty('ready', True)
        self.generate_button.setToolTip("<html><head/><body><p>Press to generate the dataset</p></body></html>")
        self.generate_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.generate_button.clicked.connect(self.checkGeneration)
        bar_layout.addWidget(self.generate_button, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        
        # Progress Bar  
# =============================================================================
#         self.bar = QProgressBar(self) 
#         self.bar.setAlignment(QtCore.Qt.AlignCenter) 
#         self.bar.setFixedWidth(280)
#         self.bar.setFont(QtGui.QFont('Arial', 9)) 
#         self.bar.setValue(0) 
#         self.bar.setVisible(False)
#         bar_layout.addWidget(self.bar, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
# =============================================================================
       
        self.progress_report = QLabel("", self)
        self.progress_report.setFont(QtGui.QFont('Arial', 11)) 
        self.progress_report.setFont(self.features_font)
        self.progress_report.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)   
        bar_layout.addWidget(self.progress_report)
        
        report_layout = QHBoxLayout()
        report_layout.addLayout(bar_layout)
        
        return report_layout
    
################################ FUNCTIONS ###############################
    # Adds families to comboBox
    def addFamily(self, selected_families, label):
        families = ""
        counter = 0
        
        for i in range(selected_families.count()):
            #print(str(selected_families.itemText(i)) + " " + str(selected_families.item_checked(i)))
            if selected_families.item_checked(i):     
                if families == "":
                    families += str(selected_families.itemText(i))
                elif families != "" and counter < selected_families.limit:
                    families += " - " +  str(selected_families.itemText(i)) 
                counter += 1
                
        if families == "":
            families = "Random"
               
        print("fam", families)     
        label.setText(families)
                    
    # Sets the suspicious counters in the Options Tab
    def setSuspiciousCountries(self, country, layout, days_off_combo, initial):
        
        self.sus_countries[country] = {}
        self.sus_countries[country]['widget label country'] = None
        self.sus_countries[country]['widget country'] = None
        self.sus_countries[country]['widget label start date'] = None
        self.sus_countries[country]['widget start date'] = None
        self.sus_countries[country]['widget label end date'] = None
        self.sus_countries[country]['widget end date'] = None
        self.sus_countries[country]['widget label day off'] = None
        self.sus_countries[country]['widget day off'] = None
        
        suspicious_countries_layout = QHBoxLayout()
        self.country_label = QLabel("Country:" , self) 
        self.country_label.setFont(self.features_font)
        self.sus_countries[country]['widget label country'] = self.country_label
        self.country_widget = QLabel(country , self) 
        self.sus_countries[country]['widget country'] = self.country_widget
          
        self.country_start_date_label = QLabel("Start Date:", self)
        self.country_start_date_label.setFont(self.features_font)
        self.sus_countries[country]['widget label start date'] = self.country_start_date_label
        
        if initial:
            self.country_start_date = QLabel(str(Variables.suspicious_countries[country]['start']) , self) 
        else:
            self.country_start_date = QLabel(str(self.sus_countries_start_time.text()) , self) 
        self.sus_countries[country]['widget start date'] = self.country_start_date
            
        self.country_end_date_label = QLabel("End Date:", self)
        self.country_end_date_label.setFont(self.features_font)
        self.sus_countries[country]['widget label end date'] = self.country_end_date_label
        
        if initial:
            self.country_end_date = QLabel(str(Variables.suspicious_countries[country]['end']), self) 
        else:
            self.country_end_date = QLabel(str(self.sus_countries_end_time.text()), self) 
        self.sus_countries[country]['widget end date'] = self.country_end_date
            
        self.country_days_off_label = QLabel("DaysOff:", self)
        self.country_days_off_label.setFont(self.features_font)
        self.sus_countries[country]['widget label day off'] = self.country_days_off_label
        
        if initial:
            self.country_days_off = QLabel(str(Variables.suspicious_countries[country]['dayoff']), self) 
        else:
            self.country_days_off = QLabel(str(self.getPickedDaysOff(days_off_combo)), self) 
        self.sus_countries[country]['widget day off'] = self.country_days_off
      
        suspicious_countries_layout.addWidget(self.country_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_widget, alignment=Qt.AlignLeft )
        suspicious_countries_layout.addWidget(self.country_start_date_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_start_date, alignment=Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_end_date_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_end_date, alignment=Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_days_off_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        suspicious_countries_layout.addWidget(self.country_days_off, alignment=Qt.AlignVCenter)
        layout.addLayout(suspicious_countries_layout)
    
    # Adds all the suspicioues countries
    def addAllSuspiciousCountries(self, countries_combo, days_off_combo, scroll_layout):
        
        for country in Variables.suspicious_countries:
            
            country_index = countries_combo.findText(country)
            country_item = countries_combo.model().item(country_index, 0)
            country_item.setCheckState(Qt.Checked)
            countries_combo.setCurrentIndex(country_index)
            
            if country is list(Variables.suspicious_countries.keys())[-1]:
                for dayoff in Variables.suspicious_countries[country]['dayoff']:
                    dayoff_index = days_off_combo.findText(dayoff)
                    dayoff_item = days_off_combo.model().item(dayoff_index, 0)
                    dayoff_item.setCheckState(Qt.Checked)
                    
            self.setSuspiciousCountries(country, scroll_layout, days_off_combo, True)
    
    # Adds a single country
    def addSingleSuspiciousCountry(self, suspicious_countries_combobox, days_off_combo, scroll_layout):
        
        country = suspicious_countries_combobox.itemText(suspicious_countries_combobox.currentIndex())
        
        if suspicious_countries_combobox.item_checked(suspicious_countries_combobox.currentIndex()):   
            self.setSuspiciousCountries(country, scroll_layout, days_off_combo, False)
            #print(self.sus_countries)
        else:
            self.removeCountry(country)
    
    # Updates the days off combobox of the countries
    def updateCountryDaysOffComboBox(self, actions_combo, days_off_combo):
        
        for i in range(days_off_combo.count()):
            if actions_combo.currentIndex() == 0:
                item = days_off_combo.model().item(i, 0)
                item.setCheckState(Qt.Checked)
            elif actions_combo.currentIndex() == 1:
                item = days_off_combo.model().item(i, 0)
                item.setCheckState(Qt.Unchecked)
            else:
                item = days_off_combo.model().item(i, 0)
                item.setCheckState(Qt.Unchecked)
                
                checks = [Qt.Checked, Qt.Unchecked]
                item_choice = random.choices(checks)[0]
                item = days_off_combo.model().item(i, 0)
                item.setCheckState(item_choice)
                
    # Get a string of the days off selected
    def getPickedDaysOff(self, days_off_combo):
        
        days_off = ""
        
        for i in range(days_off_combo.count()):
            #print(i)
            if days_off_combo.item_checked(i):
                if i == days_off_combo.count() - 1:
                    days_off += " and "
                else:
                    if days_off != "":
                        days_off += ", "
                days_off += days_off_combo.itemText(i)
        
        if days_off == "":
            days_off = "---"
                    
        return days_off
    
    # Removes a certain country
    def removeCountry(self, country):
        #print("Country " + str(country) + " was unchecked!")
        self.sus_countries[country]['widget label country'].setParent(None)
        self.sus_countries[country]['widget country'].setParent(None)
        self.sus_countries[country]['widget label start date'].setParent(None)
        self.sus_countries[country]['widget start date'].setParent(None)
        self.sus_countries[country]['widget label end date'].setParent(None)
        self.sus_countries[country]['widget end date'].setParent(None)
        self.sus_countries[country]['widget label day off'].setParent(None)
        self.sus_countries[country]['widget day off'].setParent(None)
        del(self.sus_countries[country]) 
        
# =============================================================================
#     # Compares the real and generated datasets
#     def analyseDatasets(self):
#         
#         Code.Generator..DatasetAnalyser.plotStatistics("generated", "Output/generatedDataset.txt")
#         Code.Generator..DatasetAnalyser.plotStatistics("real", "realDatasetCleaned.txt")
#         
#         for i in self.subwindows:
#                 i.close()       
#         self.close()
# =============================================================================
        
    # Compares the Queue and Speed generation Mode
    def analyseDatasets(self, mode):
        
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a generator object
        self.statistics = Statistics(mode)
        # Step 4: Move generator to the thread
        self.statistics.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.statistics.run)
        self.statistics.finished.connect(self.thread.quit)
        self.statistics.finished.connect(self.statistics.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.statistics.progress.connect(self.signal_accept)
        # Step 6: Start the thread
        self.thread.start()
        
        # Final resets
        self.thread.finished.connect(self.close)     
        
    # Closes windows
    def closeTool(self):
        for i in self.subwindows:
            i.close()       
        self.close()
    
    # Opens a new window (Teams or Areas)
    def newSubWindow(self, windowType, domain):
        
        subwindow_found = False
        
        for i in self.subwindows:
            if i.type == windowType:
                subwindow_found = True
                if windowType == "Areas":
                    print("The area window is already opened!")
                elif windowType == "Analysts":
                    print("The analysts window is already opened!")
                break
        
        if not subwindow_found:
            sub_window = SubWindow(self, windowType, domain)
            sub_window.window().resize(620, 500)
            self.subwindows.append(sub_window)
            sub_window.show()
    
    # Locks the ability to change the start and end time
    def lockDates(self, widget):
        
        if widget.isEnabled():
            print("Dates customization disabled!") 
            widget.setEnabled(False)
            self.sus_countries_lock.setProperty("locked", True) 
            self.sus_countries_lock.setStyle(self.sus_countries_lock.style())    
        else:
            print("Dates customization enabled!")
            widget.setEnabled(True)
            self.sus_countries_lock.setProperty("locked", False) 
            self.sus_countries_lock.setStyle(self.sus_countries_lock.style())
    
    # Setups the different areas
    def addAreas(self, domains):
        
        for i in range(0, len(domains)):         
            self.domain_options.addItem(domains[i])
            if Configurator.checkConfigFile(domains[i]):
                icon = QtGui.QIcon('./Resources/Icons/existent.png')
            else:
                icon = QtGui.QIcon('./Resources/Icons/inexistent.png')
                     
            self.domain_options.setItemIcon(i, icon)
            self.domain_options.setIconSize(QtCore.QSize(10, 10))
    
    # Changes the domain being analysed. The default is Cybersecurity
    def changeDomain(self, domain):
        
        if Configurator.checkConfigFile(domain):               
            if not Configurator.loadInitConfig(domain):
                Configurator.loadInitConfig("Cybersecurity")            
                index = self.domain_options.findText("Cybersecurity", QtCore.Qt.MatchFixedString)
                self.domain_options.setCurrentIndex(index)
                print("Cybersecurity configuration file successfully loaded!")
            else:
                print("Domain changed!")
                for i in range(self.sus_countries_combo.count()):
                    if self.sus_countries_combo.item_checked(i):          
                        item = self.sus_countries_combo.model().item(i, 0)
                        item.setCheckState(Qt.Unchecked)
                        self.removeCountry(item.text())
        else:
            InterfaceUtils.message(self, "Error", "The configuration file of " + domain + " not found!")
            index = self.domain_options.findText("Cybersecurity", QtCore.Qt.MatchFixedString)
            self.domain_options.setCurrentIndex(index)
            if Configurator.loadInitConfig("Cybersecurity"):
                print("Cybersecurity configuration file successfully loaded!")
            
        if Variables.suspicious_selector:
            self.addAllSuspiciousCountries(self.sus_countries_combo, self.sus_days_off_combo, self.scroll_content_layout)

        self.track_behaviour_toggle.setChecked(Variables.suspicious_selector)
        self.sus_countries_groupbox.setEnabled(Variables.suspicious_selector)
    
    # Changes the domain being analysed. The default is Cybersecurity
    def changeFormat(self, file_format):
        
        Variables.format_selected_idx = file_format
        print(file_format)
        print("Variables ip selected:", str(self.format_options.currentText()))

    # Sets the default family (Follows normal distribution)
    def distributionMode(self, d):
        
        if d.text() == "Normal":
            if d.isChecked() == True:
                print("Normal distributions activated!")
                self.week_generation.setEnabled(True)
                self.time_generation.setEnabled(True)            
                Variables.distribution_mode = "normal"
        
        if d.text() == "Uniform":
            if d.isChecked() == True:
                print("Uniform distribution activated!")
                self.week_generation.setEnabled(False)
                self.time_generation.setEnabled(False)
                Variables.distribution_mode = "uniform"
                
    # Changes the option of having all shifts occupied
    def changeUserInfo(self, users_info):
        
        if users_info.isChecked():
            print("Reset Users Info")
            Variables.reset_user_shift_daysoff = True
            print(Variables.reset_user_shift_daysoff)
        else:
            print("Users Info not changed")
            Variables.reset_user_shift_daysoff = False
            print(Variables.reset_user_shift_daysoff)
    
    # Changes the option of using default families
    def familyDefaultMode(self, d):
	
        if d.isChecked():
            print("Default Families actived!")
            self.distribution_groupbox.setEnabled(False)
            Variables.family_default_mode = True
            Variables.default_alert_pool = Configurator.readCustomConfigSection(self.domain_options.currentText(), "families")
        else:
            print("Default Families not actived!")
            self.distribution_groupbox.setEnabled(True)
            Variables.family_default_mode = False
            Variables.default_alert_pool = {}
        self.distributionMode(self.family_distribution_normal)
            
    # Changes the option of detecting attacks from different natures
    def multipleAttackMode(self, d):
	
        if d:
            print("Attacks with different natures!")
            #self.coordinated_attacks_groupbox.setEnabled(True)
            Variables.multiple_attack_selector = True
        else:
            print("Attacks with only one nature!")
            #self.coordinated_attacks_groupbox.setEnabled(False)
            Variables.multiple_attack_selector = False
    
    # Get the address picked by the user
    def pickIPaddress(self, i):
        
        Variables.ip_selected_idx = i
        print("Variables ip selected:", str(self.ip_type.currentText()))  
    
    # Updates the start and end time of the tickets
    def updateTicketDates(self, stage):
        
        if stage == "initial datetime":
            Variables.start_date = self.date_init_input.text()
            print("New initial datetime:", Variables.start_date)
        elif stage == "end datetime":
            Variables.end_date = self.date_end_input.text()   
            print("New end datetime:", Variables.end_date)
    
    # Changes the time probability of the families
    def timeMode(self, t):
	
        if t.isChecked():
            print("In terms of time, all Families have the same probability")
            Variables.time_probabilities_mode = True
            self.spin_time_day_light.setEnabled(False)
            self.spin_time_night_light.setEnabled(False)
        else:
            print("Families will have different probabilities during the time of the day")
            Variables.time_probabilities_mode = False
            self.spin_time_day_light.setEnabled(True)
            self.spin_time_night_light.setEnabled(True)
                
    # Changes the week probability of the families
    def weekMode(self, w):
	
        if w.isChecked():
            print("In terms of the day, all Families have the same probability")
            Variables.week_equal_probabilities = True
            self.spin_weekend.setEnabled(False)
            self.spin_week.setEnabled(False)
        else:
            print("Families will have different probabilities during the week")
            Variables.week_equal_probabilities = False
            self.spin_weekend.setEnabled(True)
            self.spin_week.setEnabled(True)
            
    # Updates the families time probabilities
    def updateTimeFamiliesProbs(self, label, prob):
	
        if label.text() == "Higher on Daylight":
            print("Time prob:", prob.value())
            time_light_prob = float (prob.value()/3)
            print("Time Day prob:", time_light_prob)
            Variables.family_time_4h[2]['prob'] = time_light_prob
            Variables.family_time_4h[3]['prob'] = time_light_prob
            Variables.family_time_4h[4]['prob'] = time_light_prob
              
            time_night_prob = 1 - prob.value()
            print("Time night prob:", time_night_prob)
            time_night_day_prob = float (time_night_prob/3)
            print("Time night day prob:", time_night_day_prob)
            Variables.family_time_4h[0]['prob'] = time_night_day_prob
            Variables.family_time_4h[1]['prob'] = time_night_day_prob
            Variables.family_time_4h[5]['prob'] = time_night_day_prob
            self.spin_time_night_light.setValue(time_night_prob)
      
        else:
            print("Time night prob:", prob.value())
            time_night_day_prob = float (prob.value()/3)
            print("Time night day prob:", time_night_day_prob)
            Variables.family_time_4h[0]['prob'] = time_night_day_prob
            Variables.family_time_4h[1]['prob'] = time_night_day_prob
            Variables.family_time_4h[5]['prob'] = time_night_day_prob
            
            time_light_prob = 1 - prob.value()
            print("Time day prob:", time_light_prob)
            time_light_day_prob = float (time_light_prob/3)
            print("Time light day prob:", time_light_day_prob)
            Variables.family_time_4h[2]['prob'] = time_light_day_prob
            Variables.family_time_4h[3]['prob'] = time_light_day_prob
            Variables.family_time_4h[4]['prob'] = time_light_day_prob
            self.spin_time_day_light.setValue(time_light_prob)
         
    # Updates the families week probabilities 
    def updateWeekFamiliesProbs(self, label, prob):
	
        if label.text() == "Higher on Weekdays":
            print("Week prob:", prob.value())
            week_day_prob = float (prob.value()/5)
            print("Week Day prob:", week_day_prob)
            Variables.week_time[0]['prob'] = week_day_prob
            Variables.week_time[1]['prob'] = week_day_prob
            Variables.week_time[2]['prob'] = week_day_prob
            Variables.week_time[3]['prob'] = week_day_prob
            Variables.week_time[4]['prob'] = week_day_prob
              
            weekend_prob = 1 - prob.value()
            print("Weekend prob:", weekend_prob)
            weekend_day_prob = float (weekend_prob/2)
            print("Weekend Day prob:", weekend_day_prob)
            Variables.week_time[5]['prob'] = weekend_day_prob
            Variables.week_time[6]['prob'] = weekend_day_prob
            self.spin_weekend.setValue(weekend_prob)
        else:
            print("Weekend prob:", prob.value())
            weekend_day_prob = float (prob.value()/2)
            print("Weekend Day prob:", weekend_day_prob)
            Variables.week_time[5]['prob'] = weekend_day_prob
            Variables.week_time[6]['prob'] = weekend_day_prob
            
            week_day = 1 - prob.value()
            print("Week prob:", week_day)
            week_day_prob = float (week_day/5)
            print("Week Day prob:", week_day_prob)
            Variables.week_time[0]['prob'] = week_day_prob
            Variables.week_time[1]['prob'] = week_day_prob
            Variables.week_time[2]['prob'] = week_day_prob
            Variables.week_time[3]['prob'] = week_day_prob
            Variables.week_time[4]['prob'] = week_day_prob
            self.spin_week.setValue(week_day)
                
    # Updates the ticket fields (number, families and techniques)
    def updateInputs(self, mode):
        
        if mode == "Standard":
            self.ticket_train_number.setText(str(Variables.standard_params['parameters']['train_ticket']))
            self.family_number.setText(str(Variables.standard_params['parameters']['families_number']))
            self.min_subfamily_number.setText(str(Variables.standard_params['parameters']['minsubfamilies_number']))
            self.max_subfamily_number.setText(str(Variables.standard_params['parameters']['maxsubfamilies_number']))
            self.technique_number.setText(str(Variables.standard_params['parameters']['techniques_number']))
            self.min_subtechnique_number.setText(str(Variables.standard_params['parameters']['minsubtechniques_number']))
            self.max_subtechnique_number.setText(str(Variables.standard_params['parameters']['maxsubtechniques_number']))
        else:
            self.ticket_train_number.setText("")
            self.family_number.setText("")
            self.min_subfamily_number.setText("")
            self.max_subfamily_number.setText("")
            self.technique_number.setText("")
            self.min_subtechnique_number.setText("")
            self.max_subtechnique_number.setText("")
           
    # Changes the generation mode (standard and custom)
    def changeGenerationMode(self):
        
        radioButton = self.sender()
        if radioButton.text() == "Standard":
            if radioButton.isChecked() == True:
                print("Standard Mode was activated!")
                self.ticketTab.setEnabled(False)
                self.familyTab.setEnabled(False)
                self.techniquesTab.setEnabled(False)
                self.areas.setEnabled(False)
                self.teams_configs.setEnabled(False)
                self.generate_button.setEnabled(True)
                self.generate_button.setProperty('ready', True)
                self.generate_button.setStyle(self.generate_button.style())
                Variables.generation_mode = "standard"
        if radioButton.text() == "Custom":
            if radioButton.isChecked() == True:
                print("Custom Mode activated!")
                self.ticketTab.setEnabled(True)
                self.familyTab.setEnabled(True)  
                self.techniquesTab.setEnabled(True)  
                self.areas.setEnabled(True)
                self.teams_configs.setEnabled(True)
                self.generate_button.setEnabled(False)
                self.generate_button.setProperty('ready', False)        
                self.generate_button.setToolTip("<html><head/><body><p>Complete all fiedls!</p></body></html>")
                self.generate_button.setStyle(self.generate_button.style())
                Variables.generation_mode = "custom"
                
        self.updateInputs(radioButton.text())
        
    # Prints the plots 
    def printPlots(self, p):
	
        if p.isChecked():
            print("Print the families plots!")
            Variables.print_plots = True	
        else:
            print("Not printing the families plot!")
            Variables.print_plots = False
    
    # Changes the debug mode    
    def changeDebug(self, b):
	
        if b.isChecked():
            print("Debug Mode was activated!")
            Variables.debug = True	
        else:
            print("Debug Mode not activated!")
            Variables.debug = False
            
    # Changes the ticket seasonality  
    def changeTicketSeasonality(self, s):
	
        if s.isChecked():
            print("Ticket Seasonality considered!")
            Variables.ticket_seasonality_selector = True	
        else:
            print("Ticket Seasonality excluded!")
            Variables.ticket_seasonality_selector = False
                
    # Changes the family seasonality  
    def changeFamilySeasonality(self, f):
	
        if f.isChecked():
            print("Family Seasonality considered!")
            Variables.family_seasonality_selector = True	
        else:
            print("Family Seasonality excluded!")
            Variables.family_seasonality_selector = False
            
    # Changes the ip    
    def changeIP(self, b):
	
        if b.isChecked():
            print("IP included!")
            Variables.ip_selector = True	
            self.ip_groupbox.setEnabled(True)
        else:
            print("IP excluded!")
            Variables.ip_selector = False
            self.ip_groupbox.setEnabled(False)
            
    # Changes the tracking mode    
    def suspiciousMode(self, b):
        if b.isChecked():
            print("Track suspicious behaviours enabled!")
            Variables.suspicious_selector = True	
            self.sus_countries_groupbox.setEnabled(True)
        else:
            print("Track suspicious behaviours disabled!")
            Variables.suspicious_selector = False
            self.sus_countries_groupbox.setEnabled(False)
            
    # Changes the outlier mode    
    def outlierMode(self, b):
        if b.isChecked():
            print("Outliers included!")
            Variables.outlier_selector = True	
            self.outlier_groupbox.setEnabled(True)
        else:
            print("Outliers excluded!")
            Variables.outlier_selector = False
            self.outlier_groupbox.setEnabled(False)
    
    # Updates the escalation frequency  
    def updateEscalateRate(self, rate):
        self.escalation_rate_label.setText(f"Rate: {rate}%")
        Variables.escalate_rate_percentage = rate
        
    # Updates the coordinated attack frequency  
    def updateCoordinatedRate(self, rate):
        self.coordinated_attacks_rate_label.setText(f"Rate: {rate}%")
        Variables.coordinated_attack_percentage = rate
        
    # Updates the subtechnique rate duration   
    def updateSubTechniqueRate(self, slider, label):
        
        #print("slider", slider.value())
        #print("label", label)
        
        label.setText(f"Rate: {slider.value()}%")
        
        if label.objectName() == "min_sub":
            #print("Min selected")
            Variables.min_subtechnique_rate = slider.value()
            self.max_subtechnique_slider.setMinimum(slider.value() + 1)
        else:
            #print("Max selected")
            Variables.max_subtechnique_rate = slider.value()
            self.min_subtechnique_slider.setMaximum(slider.value() - 1)
            
    # Updates the subtechnique cost   
    def updateSubTechniqueCost(self, slider, label):
        
        #print("slider", slider)
        #print("slider value", slider.value())
        #print("label", label.text())
        
        label.setText(f"Cost: {slider.value()}")
        #print("label updated", label.text())
        
        if label.objectName() == "min_sub_cost":
            print("Min selected")
            Variables.min_subtechnique_cost = slider.value()
            print("Max selected")
            Variables.max_subtechnique_cost = slider.value()

        print("Min cost", Variables.min_subtechnique_cost)
        print("Max cost", Variables.max_subtechnique_cost)
        
    # Updates detection time range   
    def updateDetectionTimeRange(self, slider, label):
        
        label.setText(f"{slider.value()} minutes")
        
        if label.objectName() == "min_time_detection":
            print("Min selected")
            Variables.min_coordinated_attack_minutes = slider.value()
        else:
            print("Max selected")
            Variables.max_coordinated_attack_minutes = slider.value()

        print("Min time", Variables.min_coordinated_attack_minutes)
        print("Max time", Variables.max_coordinated_attack_minutes)
        
    # Updates the outlier frequency  
    def updateOutlierRate(self, rate):
        self.outlier_rate_output.setText(f"Frequency Rate: {rate}%")
        Variables.outlier_rate = rate
        
    # Updates the outlier impact  
    def updateOutlierValue(self, val):
        print("Outlier Percentage:", val)
        Variables.outlier_cost = val
        
    # Updates the rate of suspicious subfamilies
    def updateCountrySubfamily(self, val):
        print("Suspicious Subfamilies Percentage:", round(val, 2))
        Variables.suspicious_subfamily = val
        
    # Verifies if the input meet certain conditions
    def checkInput(self, widget):
         
        if widget.objectName() == "ticket_train":
            if widget.text():
                tickets = int(self.ticket_train_number.text())
                #print("Aqui")
                if tickets < 1:
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "The number of training tickets must be greater than 0!")
                    return
                
        elif widget.objectName() == "family_number":
            if widget.text():
                families = int(self.family_number.text())
                if not (1 <= families <= len(string.ascii_uppercase)):
                    widget.setText("")
                    self.selectable_families_combo.setEnabled(False)
                    InterfaceUtils.message(self, "Error", "Valid range of the number of families is 1-" + str(len(string.ascii_uppercase)))
                    return
                else:
                    self.selectable_families_combo.limit = int(self.family_number.text())
                    self.selectable_families_combo.reset_items()
                    self.selected_families.setText("Random")
                    self.selectable_families_combo.setEnabled(True)
                
        elif widget.objectName() == "minimum_subFamilies":
            if widget.text():
                min_subfamilies = int(self.min_subfamily_number.text())
                if not (1 <= min_subfamilies <= 4):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the minimum number of families is 1-4")
                    return
                
        elif widget.objectName() == "maximum_subFamilies":
            if widget.text():
                max_subfamilies = int(self.max_subfamily_number.text())
                if not (5 <= max_subfamilies <= 11):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the maximum number of subfamilies is 5-11")
                    return
    
        elif widget.objectName() == "minimum_attack_occurences":
            if widget.text():
                min_attacks = int(self.min_occurences_number.text())
                if not (1 <= min_attacks <= 2):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the minimum attack occurences of the subfamilies is 1-3")
                    return
                
        elif widget.objectName() == "maximum_attack_occurences":
            if widget.text():
                max_attacks = int(self.max_occurences_number.text())
                if not (2 <= max_attacks <= 5):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the maximjm attack occurences of the subfamilies is 4-6")
                    return
                
        elif widget.objectName() == "techniques_number":
            if widget.text():
                techniques = int(self.technique_number.text())
                if not (1 <= techniques <= 62):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the number of techniques is 1-62")
                    self.min_subtechnique_number.setEnabled(False)
                    self.max_subtechnique_number.setEnabled(False)
                    return
                else:
                    self.min_subtechnique_number.setEnabled(True)
                    self.max_subtechnique_number.setEnabled(True)
            else:
                self.min_subtechnique_number.setEnabled(False)
                self.max_subtechnique_number.setEnabled(False)
                    
        elif widget.objectName() == "min_subtechnique":
            if widget.text():
                techniques = int(self.technique_number.text())
                min_subtechniques = int(self.min_subtechnique_number.text())
                if not (1 <= min_subtechniques <= (255//techniques)):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the minimum number of subtechniques is: 1-" + str(255//techniques))
                    return
                
        elif widget.objectName() == "max_subtechnique":
            if widget.text():
                techniques = int(self.technique_number.text())
                min_subtechniques = int(self.min_subtechnique_number.text())
                max_subtechniques = int(self.max_subtechnique_number.text())
                if not (min_subtechniques <= max_subtechniques <= ((255//techniques) + min_subtechniques)):
                    widget.setText("")
                    InterfaceUtils.message(self, "Error", "Valid range of the maximum number of subtechniques is: " + str(min_subtechniques) + "-"+ str(((255//techniques) + min_subtechniques)))
                    return
                
        # IF all are complete turn the button to green
        if self.ticket_train_number.text() and self.family_number.text() and self.min_subfamily_number.text() and self.max_subfamily_number.text() and self.technique_number.text() and self.min_subtechnique_number.text() and self.max_subtechnique_number.text():
            self.generate_button.setProperty('ready', True)
            self.generate_button.setStyle(self.generate_button.style())
            self.generate_button.setToolTip("<html><head/><body><p>Press to generate the dataset!</p></body></html>")
            self.generate_button.setEnabled(True)
            
    # Updates probability of using the subfamily action
    def updateAnalystProbSubfamily(self, val):
        print("The probability of using the subfamily action was changed to:", round(val, 2))
        Variables.analyst_subfamily_action_probability = val
        
    # Updates probability of using the same action
    def updateSameAnalystAction(self, val):
        print("The probability of using the same action was changed to:", round(val, 2))
        Variables.analyst_same_action_probability = val
            
    # Generates the dataset according to the mode selected
    def checkGeneration(self):
        
        #print("\014")
        
        Variables.suspicious_countries = self.sus_countries
        
        if self.generation_custom.isChecked():
            
            train_tickets = self.ticket_train_number.text()
            families = self.family_number.text()
            families_types = self.selected_families.text()
            min_subfamilies = self.min_subfamily_number.text()
            max_subfamilies = self.max_subfamily_number.text()
            techniques = self.technique_number.text()
            min_techniques = self.min_subtechnique_number.text()
            max_techniques = self.max_subtechnique_number.text()
            
            print("Number of train tickets: ", train_tickets)
            print("Number of Families: ", families)
            print("Types of Families: ", families_types)
            print("Minimum number of Families: ", min_subfamilies)
            print("Maximum number of Families: ", max_subfamilies)
            print("Number of Techniques: ", techniques)
            print("Minimum number of sub techniques: ", min_techniques)
            print("Maximum number of sub techniques: ", max_techniques)
          
            self.datasetgen(self.domain_options.currentText(), train_tickets, families, families_types, min_subfamilies, max_subfamilies, techniques, min_techniques, max_techniques)    
        else:
            Variables.default_alert_pool = Configurator.readCustomConfigSection(self.domain_options.currentText(), "families")
            Variables.suspicious_countries = self.sus_countries
            self.datasetgen(self.domain_options.currentText(), Variables.standard_params['parameters']['train_ticket'], Variables.standard_params['parameters']['families_number'], "Random", Variables.standard_params['parameters']['minsubfamilies_number'], Variables.standard_params['parameters']['maxsubfamilies_number'], Variables.standard_params['parameters']['techniques_number'], Variables.standard_params['parameters']['minsubtechniques_number'],  Variables.standard_params['parameters']['maxsubtechniques_number'])
           
    # Updates the generation status
    def signal_accept(self, msg):
        #self.bar.setValue(msg)
        if msg < 10:
            self.progress_report.setText("Generating Families...")
        elif msg < 30:
            self.progress_report.setText("Creating Tickets Basic Data...")
        elif msg < 35:
            self.progress_report.setText("Generating actions for Families and Subfamilies...")
        elif msg < 40:
            self.progress_report.setText("Assigning Teams and Analysts to Tickets...")
        elif msg < 55:
            self.progress_report.setText("Finding similar and coordinated Tickets...")
        elif msg < 60:
            self.progress_report.setText("Finding Analysts available for Tickets...")
        elif msg < 75:
            self.progress_report.setText("Allocating Analysts to Tickets...")
        elif msg < 80:
            self.progress_report.setText("Completing the Tickets Data...")
        elif msg < 100:
            self.progress_report.setText("Saving Tickets into an excel file...")
        elif msg == 100:
            self.progress_report.setText("Dataset Generation Completed")
          
    # Resumes the generation button after outputing the dataset          
    def resumeGenButton(self):
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate")
        #self.bar.setValue(0)
        #self.bar.setVisible(False)
        self.progress_report.setText("")
    
    # Redefined version of the window close event
    def closeEvent(self, event):
        try:
            for i in self.subwindows:
                i.close()
            
            if self.generator:
                self.generator.canceled = True
    
            print("Application closed successfully!\n")
        except AttributeError:
            print("Application closed successfully. No threads were running!\n")
            
    # Calls the Generator Class to build the dataset in a thread
    def datasetgen(self, domain, train_tickets, families, families_types, min_families, max_families, techniques, min_techniques, max_techniques):
        
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a generator object
        self.generator = Generator(domain, train_tickets, families, families_types, min_families, max_families, techniques, min_techniques, max_techniques)
        # Step 4: Move generator to the thread
        self.generator.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.generator.run)
        self.generator.finished.connect(self.thread.quit)
        self.generator.finished.connect(self.generator.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.generator.progress.connect(self.signal_accept)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.generate_button.setText("Generating...")
        self.generate_button.setEnabled(False)
        #self.bar.setVisible(True)
        self.thread.finished.connect(self.resumeGenButton)        

if __name__ == '__main__':
    print("\014")
    os.chdir("../../")
    #print("Initial path:", os.getcwd())

    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    #app = QApplication(sys.argv)
    win = MainWindow()

    qr = win.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    win.move(qr.topLeft()) 
    #win.move(win.pos().x()-240, win.pos().y() - 380)
    win.move(win.pos().x(), win.pos().y() - 180)

    win.show()
    sys.exit(app.exec())