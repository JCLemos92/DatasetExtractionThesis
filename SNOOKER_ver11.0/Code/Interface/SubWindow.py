# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 15:01:46 2021

@author: Leonardo Ferreira
@goal: Interface for the personalization of the analysts and incidents 
"""

from Code.Variables import Variables
from Code.Configurator import Configurator
from CheckableComboBox import CheckableComboBox 
from InterfaceUtils import InterfaceUtils 

from PyQt5 import QtGui
import random
from functools import partial
from fractions import Fraction
from os import path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QApplication,
    QSizePolicy,
    QScrollArea,
    QPushButton,
    QRadioButton,
    QGroupBox,
    QSlider,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
)

# Subwindow class
class SubWindow(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.parent_windows = self.args[0]
        self.type = self.args[1]
        self.domain = self.args[2]
        
        self.setWindowIcon(QtGui.QIcon('./Resources/Icons/tkinter_icon.ico'))
        InterfaceUtils.widgetsSetStyle(self, "Styles\style.css")
        InterfaceUtils.setFonts(self)
            
        self.standard_teams = {}
        self.custom_teams = {}
        self.analysts = {}
        self.standard_areas = {}
        self.custom_areas = {}
        self.incidents = {}
        self.setupSubUi()   
        
    # Setups the Subwindow UI
    def setupSubUi(self):
        
        self.centralWidget = QWidget()
        main_layout = QVBoxLayout(self.centralWidget)
        
        if self.type == "Analysts":
            self.setWindowTitle("Teams and Analysts Configurator")

            generation_layout = QHBoxLayout()
            self.team_modes = QGroupBox("Team Generation Mode:", self)
            self.team_modes.setLayout(generation_layout)
            self.team_modes.setFont(self.features_font)
            self.team_standard = QRadioButton("Standard")
            self.team_standard.setChecked(True)
            self.team_standard.toggled.connect(lambda:self.teamMode(self.team_standard, main_layout))
            
            self.team_custom = QRadioButton("Custom")
            self.team_custom.toggled.connect(lambda:self.teamMode(self.team_custom, main_layout))

            # Team Allocation Type QCheckBox
            self.team_allocation_type = QCheckBox("Prioritize Lower Teams")
            self.team_allocation_type.setHidden(True)
            self.team_allocation_type.setChecked(Variables.lower_teams)
            self.team_allocation_type.setLayoutDirection(Qt.RightToLeft) 
            self.team_allocation_type.stateChanged.connect(lambda:self.TeamsPrioritizationMode(self.team_allocation_type))
            
            # Shift QCheckBox
            self.shifts = QCheckBox("Use all shifts")
            self.shifts.setHidden(True)
            self.shifts.setChecked(Variables.allshifts_occupied)
            self.shifts.setLayoutDirection(Qt.RightToLeft) 
            self.shifts.stateChanged.connect(lambda:self.shiftsMode(self.shifts))
            
            generation_layout.addWidget(self.team_standard, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            generation_layout.addWidget(self.team_custom, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
            generation_layout.addWidget(self.team_allocation_type, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            generation_layout.addWidget(self.shifts, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
            main_layout.addWidget(self.team_modes)
        
            self.initStandardTeams(main_layout)
            self.teamsInfo(main_layout)
            self.analystsInfo(main_layout)        
        else:
            self.setWindowTitle("Incident Area Configurator")
            
            generation_layout = QHBoxLayout()
            self.area_modes = QGroupBox("Area Generation Mode:", self)
            self.area_modes.setLayout(generation_layout)
            self.area_modes.setFont(self.features_font)
            self.area_standard = QRadioButton("Standard")
            self.area_standard.setChecked(True)
            self.area_standard.toggled.connect(lambda:self.incidentMode(self.area_standard, main_layout))
            
            self.area_custom = QRadioButton("Custom")
            self.area_custom.toggled.connect(lambda:self.incidentMode(self.area_custom, main_layout))
            
            generation_layout.addWidget(self.area_standard, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            generation_layout.addWidget(self.area_custom, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
            
            main_layout.addLayout(generation_layout)
            main_layout.addWidget(self.area_modes)
                   
            groupbox_pos = 0
            
            for area_type in Variables.incident_area[self.domain].keys():
                
                self.area = Variables.incident_area[self.domain][area_type]['type']
                self.standard_areas[self.area] = {}
                self.standard_areas[self.area]['probs'] = Variables.incident_area[self.domain][area_type]['prob']
                
                area_layout = QGridLayout()
                self.standard_areas_groupbox = QGroupBox(self.area, self)
                self.standard_areas_groupbox.setFont(self.features_font)
                self.standard_areas_groupbox.setLayout(area_layout)
                
                standard_areas_layout = QHBoxLayout()
                self.curr_area_label = QLabel("Probability", self.standard_areas_groupbox)
                self.standard_areas[self.area]['groupbox widget'] = self.standard_areas_groupbox
                    
                spin_incident_area = QDoubleSpinBox(self.standard_areas_groupbox)
                spin_incident_area.setAlignment(Qt.AlignCenter)
                spin_incident_area.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
                self.standard_areas[self.area]['widget spin'] = spin_incident_area
                self.standard_areas[self.area]['layout'] = standard_areas_layout
                spin_incident_area.setRange(0, 1)
                spin_incident_area.setValue(Variables.incident_area[self.domain][area_type]['prob'])
                spin_incident_area.setSingleStep(0.01)
                
                self.area_check = QPushButton(self.standard_areas_groupbox)
                self.area_check.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
                self.area_check.setObjectName("incident_lock")
                self.area_check.setProperty("locked", False)  
                
                if Variables.incident_area[self.domain][area_type]['prob'] == 0:
                    spin_incident_area.setEnabled(False)
                    self.area_check.setProperty("locked", True)  
                    self.area_check.setStyle(self.area_check.style())
                else:
                    self.area_check.setProperty("locked", False)
                    self.area_check.setStyle(self.area_check.style())
                
                self.area_check.pressed.connect(partial(self.areaMode, self.area_check, self.area, spin_incident_area))
                self.standard_areas[self.area]['checkbox'] = self.area_check
                spin_incident_area.valueChanged.connect(lambda value = spin_incident_area.value(), area_type = area_type:self.changeAreaProbs(area_type, value))
      
                standard_areas_layout.addWidget(self.curr_area_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
                standard_areas_layout.addWidget(spin_incident_area, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
                standard_areas_layout.addWidget(self.area_check, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
                area_layout.addLayout(standard_areas_layout, groupbox_pos, 0)
                
                groupbox_pos += 1
                main_layout.addWidget(self.standard_areas_groupbox)
                
            self.areasInfo(main_layout, self.domain)
        
        self.setWidget(self.centralWidget)
        self.setWidgetResizable(True)
        
    # Sets the UI of the incidents input
    def areasInfo(self, main_layout, area_chosen):
        
        area_input_layout = QHBoxLayout()
        area_input_layout.setSpacing(20)
        
        self.incident_area_input = QGroupBox("Incident Input", self)
        self.incident_area_input.setFont(self.features_font)
        self.incident_area_input.setLayout(area_input_layout)
        self.incident_area_input.setHidden(True)
        main_layout.addWidget(self.incident_area_input)

        self.curr_incident_area_label = QLabel("New incident:", self)
        self.curr_incident_area = QLineEdit()
        self.curr_incident_area.setFixedWidth(160)
        
        self.curr_prob_label = QLabel("Probability", self)
        self.curr_prob_spin = QDoubleSpinBox()
        self.curr_prob_spin.setAlignment(Qt.AlignCenter)
        self.curr_prob_spin.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.curr_prob_spin.setRange(0.01, 1)
        self.curr_prob_spin.setValue(round(random.uniform(0.01, 1), 2))
        self.curr_prob_spin.setMaximum(1)
        self.curr_prob_spin.setMinimum(0.01)
        self.curr_prob_spin.setSingleStep(0.01)
       
        self.add_incident_area_button = QPushButton(self) 
        self.add_incident_area_button.setObjectName("addIncident")
        self.add_incident_area_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.add_incident_area_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))

        area_input_layout.addWidget(self.curr_incident_area_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        area_input_layout.addWidget(self.curr_incident_area)
        area_input_layout.addWidget(self.curr_prob_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        area_input_layout.addWidget(self.curr_prob_spin)
        area_input_layout.addWidget(self.add_incident_area_button)
               
        main_layout.addLayout(area_input_layout)
        
        self.save_incident_config_button = QPushButton(self) 
        self.save_incident_config_button.setObjectName("saveConfig")
        self.save_incident_config_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.save_incident_config_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.save_incident_config_button.setHidden(True)  
        
        self.load_incidents_button = QPushButton(self) 
        self.load_incidents_button.setObjectName("loadConfig")
        self.load_incidents_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.load_incidents_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.load_incidents_button.setHidden(True)  
        
        for curr_area in Variables.incident_area.keys():
            self.custom_areas = {}
            self.custom_areas[curr_area] = {}
            self.custom_areas[curr_area]['incidents'] = []   
            self.incidents[curr_area] = {}
            self.no_incidents = QLabel("No incidents created!", self) 
            self.custom_areas[curr_area]['no incidents widget'] =  self.no_incidents 
            layout = QVBoxLayout()
            self.custom_areas[curr_area]['layout'] = layout
            
            self.area = QGroupBox("Area " + str(curr_area), self)
            self.area.setFont(self.features_font)
            self.area.setLayout(layout)
            self.area.setHidden(True)
            self.custom_areas[curr_area]['groupbox widget'] = self.area
            layout.addWidget(self.no_incidents) 
            main_layout.addWidget(self.area, alignment=Qt.AlignTop)
           
        self.add_incident_area_button.clicked.connect(lambda:self.addIncidentArea(self.curr_incident_area.text(), self.curr_prob_spin.value()))
        self.save_incident_config_button.clicked.connect(self.saveIncidentsConfigurations)
        self.load_incidents_button.clicked.connect(self.loadIncidentsConfigurations)
        
        custom_buttons_layout = QHBoxLayout()
        custom_buttons_layout.addWidget(self.save_incident_config_button, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        custom_buttons_layout.addWidget(self.load_incidents_button, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        main_layout.addLayout(custom_buttons_layout)
        
################################ FUNCTIONS ###############################

    # Loads the Team Configurations
    def loadTeamsConfigurations(self):

        filename = Configurator.loadConfigWindow(self)

        if filename:

            while len(self.analysts) != 0:
                analyst_name = list(self.analysts.keys())[0]
                team = InterfaceUtils.getTeamAnalyst(self.custom_teams, analyst_name)
                self.removeAnalyst(team, analyst_name) 
                
            config_data = Configurator.readConfigFile(self.domain, filename)
            
            if Configurator.checkConfigParameter(config_data, "teams_info_pool") and Configurator.checkConfigParameter(config_data, "analysts_skills"):
                temp_teams = config_data["teams_info_pool"]
                temp_analysts = config_data["analysts_skills"]
                #print(temp_analysts)

                for analyst in temp_analysts.keys():
                    for team in temp_teams.keys():
                        if analyst in list(temp_teams[team]):
                            shift = temp_analysts[analyst]["shift"]
                            days_off = temp_analysts[analyst]["days off"]
                            value = temp_analysts[analyst]["speed"]
                            self.addAnalystInfo(analyst, team, shift, value, self.daysOffOutput(days_off))
            
                Variables.analysts_skills = temp_analysts
                Variables.teams_info_pool = temp_teams
                #print(temp_analysts)
                print("Teams loaded successfully!")
            else:
                print("Impossible to load configuration!")
            self.close()

    # Loads the Incidents Configurations
    def loadIncidentsConfigurations(self):
        
        while len(self.incidents[self.domain]) != 0:
            incident_name = list(self.incidents[self.domain].keys())[0]
            self.removeIncident(incident_name) 
            
        filename = Configurator.loadConfigWindow(self)

        if filename:
            config_data = Configurator.readConfigFile(self.domain, filename)
            temp_incidents = config_data["incident_area"]

            for incident in temp_incidents[self.domain].keys():
                incident_type = temp_incidents[self.domain][incident]['type']
                incident_prob = temp_incidents[self.domain][incident]['prob']

                if isinstance(incident_prob, str):
                    if incident_prob.find("/"):
                        incident_prob = float('%.2f' % sum(Fraction(s) for s in incident_prob.split()))
                        temp_incidents[self.domain][incident]['prob'] = incident_prob
                self.addIncidentArea(incident_type, incident_prob)

            Variables.incident_area = temp_incidents
            print("Areas loaded successfully!")
            self.close()  
            
    # Adds an incident
    def addIncidentArea(self, name, prob):    
        
        if not name:  
            InterfaceUtils.message(self, "Incident Area Building", "The name cannot be empty!")
        elif name not in self.incidents[self.domain].keys():
            self.incidents[self.domain][name] = {}
            self.incidents[self.domain][name]['widget label name'] = None
            self.incidents[self.domain][name]['widget name'] = None
            self.incidents[self.domain][name]['widget label prob'] = None
            self.incidents[self.domain][name]['widget prob'] = prob
            self.incidents[self.domain][name]['widget delete'] = None
            
            self.custom_areas[self.domain]['incidents'].append(name)
            self.custom_areas[self.domain]['no incidents widget'].setHidden(True)
        
            incidents_layout = QHBoxLayout()
            self.incident_label = QLabel("Incident:" , self) 
            self.incident_label.setFont(self.features_font)
            self.incidents[self.domain][name]['widget label name'] = self.incident_label
            self.incident = QLabel(name , self) 
            self.incidents[self.domain][name]['widget name'] = self.incident
          
            self.prob_label = QLabel("Probability:", self)
            self.prob_label.setFont(self.features_font)
            self.incidents[self.domain][name]['widget label prob'] = self.prob_label
            self.probability = QLabel(str(prob), self) 
            self.incidents[self.domain][name]['widget prob'] = self.probability
            
            self.remove_incident_button = QPushButton(self) 
            self.remove_incident_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
            self.remove_incident_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            self.remove_incident_button.setObjectName("removeIncident")
            
            self.incidents[self.domain][name]['widget delete'] = self.remove_incident_button
            self.remove_incident_button.clicked.connect(lambda:self.removeIncident(name))
            
            incidents_layout.addWidget(self.incident_label, alignment = Qt.AlignLeft)
            incidents_layout.addWidget(self.incident, alignment = Qt.AlignLeft)
            incidents_layout.addWidget(self.prob_label, alignment = Qt.AlignLeft)
            incidents_layout.addWidget(self.probability, alignment = Qt.AlignRight)
            incidents_layout.addWidget(self.remove_incident_button, alignment = Qt.AlignRight)

            layout = self.custom_areas[self.domain]['layout']
            layout.addLayout(incidents_layout)
                        
            self.curr_incident_area.setText("")
            
            if self.getIncidentsProb() >= 1:
                self.curr_prob_spin.setEnabled(False)
                self.curr_incident_area.setEnabled(False)
                self.add_incident_area_button.setEnabled(False)
            else:     
                self.curr_prob_spin.setMaximum(round(1-self.getIncidentsProb(),2))
                self.curr_prob_spin.setValue(round(random.uniform(0.1, 1-self.getIncidentsProb()), 2))
                self.curr_prob_spin.setEnabled(True)
                self.curr_incident_area.setEnabled(True)
                self.add_incident_area_button.setEnabled(True)
            
        else:
            InterfaceUtils.message(self, "Incident Area Building", "There is already an incident with the same name!")
    
    # Saves the Team Configurations
    def saveIncidentsConfigurations(self):

        message = ""

        for area in self.incidents.keys():
            if not self.incidents[area]:     
                message += "No incidents have been added.\n"
            else:   
                if self.getIncidentsProb() < 1:
                    message += "The probabilities of all the incidents is less than 1.\n"
                    for area in self.custom_areas.keys():
                        message +=  "The " + area + " area has the following incidents:\n"
                        for incident in self.custom_areas[area]['incidents']:
                            if incident is list(self.custom_areas[area]['incidents'])[-1]:
                                message += "\n"
                            message +=  "\u2022 " + incident + " - Probability = " +  self.incidents[self.domain][incident]['widget prob'].text()

        if message != "":  
            InterfaceUtils.message(self, "Incident Area Building", message)
        else:
            filename = Configurator.saveConfigWindow(self)
            temp_areas = {}
            
            for area in self.custom_areas.keys():
                temp_areas[area] = {}
                for incident in self.custom_areas[area]['incidents']:
                    incident_idx = self.custom_areas[area]['incidents'].index(incident)
                    temp_areas[area][incident_idx] = {}
                    temp_areas[area][incident_idx]['type'] = self.incidents[area][incident]["widget name"].text()
                    temp_areas[area][incident_idx]['prob'] = float(self.incidents[area][incident]['widget prob'].text())
                 
            Configurator.updateConfigFile("incident_area", temp_areas, self.domain, filename)
            Variables.incident_area[self.domain] = temp_areas[self.domain]
            print("Areas assigned successfully!")
            self.close()    
            
    # Changes the Incidents area probabilities      
    def changeAreaProbs(self, area_idx_picked, prob):
          
        areas_no_prob = False
        if Variables.incident_area[self.domain][area_idx_picked]['prob'] > prob:
            areas_no_prob = True
        
        incident_pool = []
        curr_area = Variables.incident_area[self.domain][area_idx_picked]['type']
        
        for i in self.standard_areas.keys():
            curr_idx_picked = list(self.standard_areas.keys()).index(i)
            
            area_prob = self.standard_areas[i]['widget spin'].value()
            if curr_idx_picked != area_idx_picked and not self.standard_areas[i]['checkbox'].isChecked():
                if area_prob == 0 and areas_no_prob:
                    incident_pool.append(i)
                elif area_prob != 0:
                    incident_pool.append(i)
                    
        if len(incident_pool) != 0:
            prob_sum = 0
            area_to_update = random.choices(incident_pool)[0]
            for a in self.standard_areas.keys():
                if a != area_to_update:
                    prob_sum += self.standard_areas[a]['widget spin'].value()
                    
            self.standard_areas[area_to_update]['widget spin'].setValue(1 - prob_sum) 
            if self.standard_areas[area_to_update]['widget spin'].value() == 0:
                self.standard_areas[area_to_update]['widget spin'].setEnabled(False)
                self.standard_areas[area_to_update]['checkbox'].setChecked(True)
                
            area_idx_updated = list(self.standard_areas.keys()).index(area_to_update)    
            Variables.incident_area[self.domain][area_idx_picked]['prob'] = prob
            Variables.incident_area[self.domain][area_idx_updated]['prob'] = 1 - prob_sum
            
            if (len(incident_pool) == 1 and prob_sum == 1):
            
                InterfaceUtils.message(self, "Incident Area Probabilities", "Impossible to distribute the probabilities!")

                self.standard_areas[area_to_update]['widget spin'].setEnabled(False)
                self.standard_areas[area_to_update]['checkbox'].setChecked(True)
                self.standard_areas[curr_area]['widget spin'].setEnabled(False)
                self.standard_areas[curr_area]['checkbox'].setChecked(True)
             
    # Removes a certain incident   
    def removeIncident(self, incident_name):
        
        print(" to delete incident_name", incident_name)
        (self.custom_areas[self.domain]['incidents']).remove(incident_name)
        self.incidents[self.domain][incident_name]['widget label name'].setParent(None)
        self.incidents[self.domain][incident_name]['widget name'].setParent(None)
        self.incidents[self.domain][incident_name]['widget label prob'].setParent(None)
        self.incidents[self.domain][incident_name]['widget prob'].setParent(None)
        self.incidents[self.domain][incident_name]['widget delete'].setParent(None)
        del(self.incidents[self.domain][incident_name])
        
        self.curr_prob_spin.setMaximum(1-self.getIncidentsProb())
        self.curr_prob_spin.setValue(random.uniform(0.01, 1-self.getIncidentsProb()))
        self.curr_prob_spin.setEnabled(True)
        self.curr_incident_area.setEnabled(True)
        self.add_incident_area_button.setEnabled(True)
        
        if not self.custom_areas[self.domain]['incidents']:
            self.custom_areas[self.domain]['no incidents widget'].setHidden(False)    
        
    # Sets the standard and custom incident panels
    def incidentMode(self, mode, main_layout):
        
        if mode.text() == "Standard":
            if mode.isChecked():
                for area in self.standard_areas:
                    self.standard_areas[area]['groupbox widget'].setHidden(False)
                    self.incident_area_input.setHidden(True)
                    self.save_incident_config_button.setHidden(True)
                    self.load_incidents_button.setHidden(True)  
                
                for area in self.custom_areas:
                    self.custom_areas[area]['groupbox widget'].setHidden(True)

        if mode.text() == "Custom":
            if mode.isChecked():
                for area in self.standard_areas:
                    self.standard_areas[area]['groupbox widget'].setHidden(True)
                    self.incident_area_input.setHidden(False)
                    self.save_incident_config_button.setHidden(False)
                    self.load_incidents_button.setHidden(False)  
                    
                for area in self.custom_areas:
                    self.custom_areas[area]['groupbox widget'].setHidden(False)

    # Adds a new analyst to the teams
    def addAnalystInfo(self, name, team, shift, value, daysoff):    
        
        if not name:    
            InterfaceUtils.message(self, "Analyst Building", "The name cannot be empty!")
        elif name not in self.analysts.keys():
            self.analysts[name] = {}
            self.analysts[name]['widget label name'] = None
            self.analysts[name]['widget name'] = None
            self.analysts[name]['widget label shift'] = None
            self.analysts[name]['widget shift'] = None
            self.analysts[name]['widget label speed'] = None
            self.analysts[name]['widget speed'] = None
            self.analysts[name]['widget label daysoff'] = None
            self.analysts[name]['widget daysoff'] = None
            self.analysts[name]['widget delete'] = None
            
            self.custom_teams[team]['analysts'].append(name)
            self.analysts[name]['team'] = team
        
            analyst_layout = QHBoxLayout()
    
            self.custom_teams[team]['no analysts widget'].setHidden(True)

            self.analyst_label = QLabel("Analyst:" , self) 
            self.analyst_label.setFont(self.features_font)
            self.analysts[name]['widget label name'] = self.analyst_label
            self.analyst = QLabel(name , self) 
            self.analysts[name]['widget name'] = self.analyst
            
            self.shift_label = QLabel("Shift:" , self) 
            self.shift_label.setFont(self.features_font)
            self.analysts[name]['widget label shift'] = self.shift_label
            self.shift = QLabel(str(self.curr_analyst_shift.itemText(shift)) , self) 
            self.analysts[name]['widget shift'] = self.shift
            self.analysts[name]['widget shift index'] = shift
            
            self.speed_label = QLabel("Speed:" , self) 
            self.speed_label.setFont(self.features_font)
            self.analysts[name]['widget label speed'] = self.speed_label
            self.speed = QLabel(str(value) , self) 
            self.analysts[name]['widget speed'] = self.speed
            
            self.analyst_days_off_label = QLabel("Days Off:", self)
            self.analyst_days_off_label.setFont(self.features_font)
            self.analysts[name]['widget label daysoff'] = self.analyst_days_off_label
            self.analyst_days_off = QLabel(daysoff, self) 
            self.analysts[name]['widget daysoff'] = self.analyst_days_off
            
            self.remove_analyst_button = QPushButton(self) 
            self.remove_analyst_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
            self.remove_analyst_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            self.remove_analyst_button.setObjectName("removeAnalyst")
            
            self.analysts[name]['widget delete'] = self.remove_analyst_button
            self.remove_analyst_button.clicked.connect(lambda:self.removeAnalyst(team, name))
            
            analyst_layout.addWidget(self.analyst_label, alignment = Qt.AlignLeft | Qt.AlignVCenter)
            analyst_layout.addWidget(self.analyst, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
            analyst_layout.addWidget(self.shift_label, alignment = Qt.AlignRight | Qt.AlignVCenter)
            analyst_layout.addWidget(self.shift, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
            analyst_layout.addWidget(self.speed_label, alignment = Qt.AlignRight | Qt.AlignVCenter)
            analyst_layout.addWidget(self.speed, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
            analyst_layout.addWidget(self.analyst_days_off_label, alignment = Qt.AlignRight | Qt.AlignVCenter)
            analyst_layout.addWidget(self.analyst_days_off, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
            analyst_layout.addWidget(self.remove_analyst_button, alignment = Qt.AlignRight | Qt.AlignVCenter)
            layout = self.custom_teams[team]['layout']
            layout.addLayout(analyst_layout)
                
            self.curr_analyst_name.setText("")
        else:
            InterfaceUtils.message(self, "Analyst Building", "There is already an analyst with the same name!")
                 
    # Removes a certain analyst
    def removeAnalyst(self, team, analyst_name):
        
        print("team", team)
        print(" to delete analyst_name", analyst_name)
        
        (self.custom_teams[team]['analysts']).remove(analyst_name)
        self.analysts[analyst_name]['widget label name'].setParent(None)
        self.analysts[analyst_name]['widget name'].setParent(None)
        self.analysts[analyst_name]['widget label shift'].setParent(None)
        self.analysts[analyst_name]['widget shift'].setParent(None)
        self.analysts[analyst_name]['widget label speed'].setParent(None)
        self.analysts[analyst_name]['widget speed'].setParent(None)
        self.analysts[analyst_name]['widget label daysoff'].setParent(None)
        self.analysts[analyst_name]['widget daysoff'].setParent(None)
        self.analysts[analyst_name]['widget delete'].setParent(None)
        del(self.analysts[analyst_name])
        
        if not self.custom_teams[team]['analysts']:
            self.custom_teams[team]['no analysts widget'].setHidden(False)
        
    # Sets the panel to add a new analyst
    def analystsInfo(self, main_layout):
        
        analyst_input_layout = QVBoxLayout()
        self.analysts_input = QGroupBox("Analyst Input", self)
        self.analysts_input.setFont(self.features_font)
        self.analysts_input.setLayout(analyst_input_layout)
        self.analysts_input.setHidden(True)
        main_layout.addWidget(self.analysts_input)
        
        curr_analyst_layout = QHBoxLayout()
        
        #curr_analyst_layout.setContentsMargins(0,0,280,0)
        self.curr_analyst_name_label = QLabel("Name:", self)
        self.curr_analyst_name = QLineEdit()
        self.curr_analyst_name.setObjectName("analyst_name")
        
        curr_analyst_conf_layout = QHBoxLayout()
        self.curr_analyst_team_label = QLabel("Team:", self)
        self.curr_analyst_team = QComboBox()
        curr_analyst_conf_layout.setSpacing(10)
        self.curr_analyst_team.addItems(list(Variables.teams_info_pool.keys()))
        
        self.curr_analyst_shift_label = QLabel("Shift:", self)
        self.curr_analyst_shift = QComboBox()
        self.curr_analyst_shift.addItems(["00:00-08:00", "08:00-16:00", "16:00-24:00"])
        
        self.curr_analyst_speed_label = QLabel("Speed:", self)
        self.curr_analyst_speed = QDoubleSpinBox()
        self.curr_analyst_speed.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.curr_analyst_speed.setAlignment(Qt.AlignHCenter) 
        self.curr_analyst_speed.setRange(0.1, 2)
        self.curr_analyst_speed.setValue(1)
        self.curr_analyst_speed.setSingleStep(0.1)
        
        ## Days OFF
        analyst_days_off_layout = QHBoxLayout()
        analyst_days_off_layout.setSpacing(25)
        #analyst_days_off_layout.setContentsMargins(0,0,30,0)
        self.analyst_days_off_label = QLabel("Days Off:")
        self.analyst_number_day_off_combobox = QComboBox()
        self.analyst_number_day_off_combobox.addItems(["1", "2", "3"])
        self.analyst_number_day_off_combobox.setCurrentIndex(1)
          
        self.analyst_day_off_combobox = CheckableComboBox("analyst", int(self.analyst_number_day_off_combobox.currentText()))
        
        random_day = random.sample(list(Variables.week_time.keys()), k=int(self.analyst_number_day_off_combobox.currentText()))
        for i in Variables.week_time.keys():
            self.analyst_day_off_combobox.addItem(Variables.week_time[i]['day'])
            item = self.analyst_day_off_combobox.model().item(i, 0)
            if i in random_day:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        
        self.analyst_number_day_off_combobox.currentIndexChanged.connect(self.resetDaysOff)
                
        self.random_day_off_button = QPushButton("Random DayOff", self) 
        self.random_day_off_button.setObjectName("random_day")
        self.random_day_off_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.random_day_off_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.random_day_off_button.clicked.connect(lambda:self.updateAnalystDaysOffComboBox(self.analyst_number_day_off_combobox.currentText(), self.analyst_day_off_combobox)) 
        
        analyst_days_off_layout.addWidget(self.analyst_days_off_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        analyst_days_off_layout.addWidget(self.analyst_number_day_off_combobox, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        analyst_days_off_layout.addWidget(self.analyst_day_off_combobox, alignment=Qt.AlignHCenter | Qt.AlignVCenter) 
        analyst_days_off_layout.addWidget(self.random_day_off_button, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        
        self.add_analyst_button = QPushButton(self) 
        self.add_analyst_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.add_analyst_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.add_analyst_button.setHidden(True)  
        self.add_analyst_button.setObjectName("addAnalyst")
        analyst_days_off_layout.addWidget(self.add_analyst_button)
        
        curr_analyst_layout.addWidget(self.curr_analyst_name_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        curr_analyst_layout.addWidget(self.curr_analyst_name, alignment=Qt.AlignLeft)
        
        curr_analyst_conf_layout.addWidget(self.curr_analyst_team_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        curr_analyst_conf_layout.addWidget(self.curr_analyst_team, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        curr_analyst_conf_layout.addWidget(self.curr_analyst_shift_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        curr_analyst_conf_layout.addWidget(self.curr_analyst_shift)
        curr_analyst_conf_layout.addWidget(self.curr_analyst_speed_label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        curr_analyst_conf_layout.addWidget(self.curr_analyst_speed)
        
        analyst_input_layout.addLayout(curr_analyst_layout)
        analyst_input_layout.addLayout(curr_analyst_conf_layout)
        analyst_input_layout.addLayout(analyst_days_off_layout)
               
        main_layout.addLayout(analyst_input_layout)
        self.add_analyst_button.clicked.connect(lambda:self.addAnalystInfo(self.curr_analyst_name.text(), self.curr_analyst_team.currentText(), self.curr_analyst_shift.currentIndex(), self.curr_analyst_speed.value(), self.daysOffOutput(self.getPickedDaysOff(self.analyst_day_off_combobox))))
        
        for curr_team in Variables.teams_info_pool.keys():
            #self.custom_teams[curr_team] = {}
            self.custom_teams[curr_team]['analysts'] = []   
            self.no_analysts = QLabel("No analysts created!", self) 
            self.custom_teams[curr_team]['no analysts widget'] =  self.no_analysts 
            layout = QVBoxLayout()
            self.custom_teams[curr_team]['layout'] = layout
            
            self.team = QGroupBox("Team " + str(curr_team), self)
            self.team.setFont(self.features_font)
            self.team.setLayout(layout)
            self.team.setHidden(True)
            self.custom_teams[curr_team]['groupbox widget'] = self.team
            layout.addWidget(self.no_analysts) 
            main_layout.addWidget(self.team, alignment=Qt.AlignTop)
            
        self.analyst_information = QLabel("Note: All teams should have at least three analysts!", self)
        self.analyst_information.setHidden(True)
        main_layout.addWidget(self.analyst_information, alignment=Qt.AlignTop)
        
        self.save_team_config_button = QPushButton(self)
        self.save_team_config_button.setObjectName("saveConfig")
        self.save_team_config_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.save_team_config_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.save_team_config_button.setHidden(True)  
        self.save_team_config_button.clicked.connect(self.saveTeamConfigurations)
        
        self.load_teams_button = QPushButton(self) 
        self.load_teams_button.setObjectName("loadConfig")
        self.load_teams_button.setToolTip("<html><head/><body><p>Add incident</p></body></html>")
        self.load_teams_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.load_teams_button.setHidden(True)  
        self.load_teams_button.clicked.connect(self.loadTeamsConfigurations)
        
        custom_buttons_layout = QHBoxLayout()
        custom_buttons_layout.addWidget(self.save_team_config_button, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        custom_buttons_layout.addWidget(self.load_teams_button, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
        main_layout.addLayout(custom_buttons_layout)
        
    # Sets the panel to customize teams
    def teamsInfo(self, main_layout):
        
        teams_input_layout = QVBoxLayout()
        self.teams_customizable = QGroupBox("Teams Customization", self)
        self.teams_customizable.setFont(self.features_font)
        self.teams_customizable.setLayout(teams_input_layout)
        self.teams_customizable.setHidden(True)
        
        for curr_team in Variables.teams_info_pool.keys():
            #print("Curr Team " + str(curr_team) + " has " + str(Variables.teams_frequency[curr_team]))
            self.custom_teams[curr_team] = {}
            team_layout = QHBoxLayout()
            self.custom_teams[curr_team]['team customize layout'] = team_layout
            
            self.team_label = QLabel("Team " + str(curr_team), self) 
            self.team_label.setFont(self.features_font)
            self.custom_teams[curr_team]['team label'] = self.team_label 
          
            self.team_slider = QSlider(Qt.Horizontal)
            self.team_slider.setFixedWidth(240)
            self.team_slider.setMinimum(1)
            self.team_slider.setMaximum(97)
            self.team_slider.setValue(Variables.teams_frequency[curr_team] *100)
            self.team_slider.setTickPosition(QSlider.TicksBelow)
            self.team_slider.setTickInterval(10)
            self.custom_teams[curr_team]['team slider'] = self.team_slider 
            
            self.team_percentage_label = QLabel("Percentage: " + str(self.team_slider.value()) + str("%"), self) 
            #self.team_slider_rate.setFont(self.features_font)
            self.custom_teams[curr_team]['team slider rate'] = self.team_percentage_label 
            
            team_layout.addWidget(self.team_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter)
            team_layout.addWidget(self.team_slider, alignment = Qt.AlignHCenter | Qt.AlignVCenter) 
            team_layout.addWidget(self.team_percentage_label, alignment = Qt.AlignHCenter | Qt.AlignVCenter) 
            teams_input_layout.addLayout(team_layout)
            
            self.team_slider.sliderReleased.connect(lambda team_slider = self.team_slider, percentage_label = self.team_percentage_label, : self.updateTeamFrequencyRate(team_slider, percentage_label))
        
        if self.team_allocation_type:
            self.teams_customizable.setEnabled(False)
        else:
            self.teams_customizable.setEnabled(True)
            
        #print("Temp", Variables.teams_frequency)
        
        main_layout.addWidget(self.teams_customizable)
        
    # Updates the percentage of tickets assigned to each Team
    def updateTeamFrequencyRate(self, slider, frequency):
        #print("Slider atualizado", slider)
        #print("Frequency", frequency)
        frequency.setText(f"Percentage: {slider.value()}%")
        
        slider_values = slider.value()
        update_teams = []
        
        for team in self.custom_teams.keys():
            if slider != self.custom_teams[team]['team slider']:
                update_teams.append(team)
                slider_values += self.custom_teams[team]['team slider'].value()
            else:
                Variables.teams_frequency[team] = slider.value()/100

        #print("Sum", slider_values)
        add = False
        if slider_values - 100 > 1:
            add = True
            total_value_update = slider_values - 100
            #print("Value to decrease on other teams", total_value_update)
        else:
            total_value_update = 100 - slider_values
            #print("Value to increase on other teams", total_value_update)
            
        while total_value_update > 0 and len(update_teams) != 0:
            
            team_to_update = random.choices(update_teams)[0]
            #print("Team to update", team_to_update)
            update_teams.remove(team_to_update)
            #print("Teams", update_teams)
            team_to_update_slider = self.custom_teams[team_to_update]['team slider']
            #print("Slider da team escolhida", team_to_update_slider.value())
            if add:
                if team_to_update_slider.value() - total_value_update < 1:
                    #print("Abaixo de 1", str(team_to_update_slider.value() - total_value_update))
                    total_value_update = abs(team_to_update_slider.value() - total_value_update) + 1
                    #print("Remanescente", total_value_update)
                    team_to_update_slider.setValue(1)
                    self.custom_teams[team_to_update]['team slider rate'].setText(f"Percentage: {team_to_update_slider.value()}%")
                else:
                    #print("Acima de 1", str(team_to_update_slider.value() - total_value_update))
                    #print("Valor a atribuir à equipa", str(team_to_update_slider.value() - total_value_update))
                    self.custom_teams[team_to_update]['team slider rate'].setText(f"Percentage: {str(team_to_update_slider.value() - total_value_update)}%")
                    team_to_update_slider.setValue(team_to_update_slider.value() - total_value_update)
                    total_value_update = 0
            else:
                if team_to_update_slider.value() + total_value_update > 97:
                    #print("Acima de 97", str(team_to_update_slider.value() + total_value_update))
                    total_value_update = 97 - team_to_update_slider.value()
                    #print("Remanescente", total_value_update)
                    team_to_update_slider.setValue(97)
                    self.custom_teams[team_to_update]['team slider rate'].setText(f"Percentage: {97}%")
                else:
                    #print("Abaixo de 97", str(team_to_update_slider.value() + total_value_update))
                    #print("Valor a atribuir à equipa", str(team_to_update_slider.value() + total_value_update))
                    self.custom_teams[team_to_update]['team slider rate'].setText(f"Percentage: {str(team_to_update_slider.value() + total_value_update)}%")
                    team_to_update_slider.setValue(team_to_update_slider.value() + total_value_update)
                    total_value_update = 0
                    
            Variables.teams_frequency[team_to_update] = team_to_update_slider.value()/100
        
        #print("Aqui", Variables.teams_frequency)

    # Resets the days off combobox of the analyst when the number of days off is changed
    def resetDaysOff(self):
        self.analyst_day_off_combobox.reset_items()
        self.analyst_day_off_combobox.limit = int(self.analyst_number_day_off_combobox.currentText())
        
    # Updates the days off combobox
    def updateAnalystDaysOffComboBox(self, limit, days_off_combo):
        all_items_text = [days_off_combo.itemText(i) for i in range(days_off_combo.count())]
        item_choice = random.sample(all_items_text, k=int(limit))
        print("Choice picked:", item_choice)
        
        for i in range(days_off_combo.count()): 
            item = days_off_combo.model().item(i, 0)
            if item.text() in item_choice:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    # Saves the Team Configurations
    def saveTeamConfigurations(self):

        message = ""
        
        for team in self.custom_teams.keys():
            if Variables.allshifts_occupied:
                shifts_available = [0, 1, 2]
                for ans in self.custom_teams[team]['analysts']:
                    analyst_shift = self.analysts[ans]['combo shift']
                    if analyst_shift in shifts_available:
                        shifts_available.remove(analyst_shift)           
                    if not shifts_available:
                        break
                if shifts_available:
                    if team is list(self.custom_teams.keys())[-1]:
                        message +=  "Team " + str(team) + " don't have analyts in the all shifts!"
                    else:
                        message += "Team " + str(team) +  ", "
            else:
                if len(self.custom_teams[team]['analysts']) < 1:
                        message += "Team " + str(team)
                        if team is list(self.custom_teams.keys())[-1]:
                            message +=  " have no analysts!"
                        else:
                            message +=  ", "
        
        if message != "":
            InterfaceUtils.message(self, "Team Building", message)
        else:
            filename = Configurator.saveConfigWindow(self)
            
            temp_teams = {}
            temp_analysts = {}
            
            for new_team in self.custom_teams.keys():
                temp_teams[new_team] = []
                temp_teams[new_team] = self.custom_teams[new_team]['analysts']
                
                for new_analyst in temp_teams[new_team]:
                    temp_analysts[new_team] = {}
                    temp_analysts[new_team][new_analyst] = {}
                    shift_index = int(self.analysts[new_analyst]["widget shift index"])
                    temp_analysts[new_team][new_analyst]['shift'] = shift_index
                    temp_analysts[new_team][new_analyst]['init'] = Variables.shifts[shift_index]['start']
                    temp_analysts[new_team][new_analyst]['end'] = Variables.shifts[shift_index]['end']
                    temp_analysts[new_team][new_analyst]['free'] = True
                    temp_analysts[new_team][new_analyst]["speed"] = round(float(self.analysts[new_analyst]["widget speed"].text()), 2)
                    temp_analysts[new_team][new_analyst]['ticket starttime'] = "None"
                    temp_analysts[new_team][new_analyst]['ticket endtime'] = "None"
                    temp_analysts[new_team][new_analyst]['days off'] = self.getPickedDaysList(self.analysts[new_analyst]["widget daysoff"].text())
                
            Configurator.updateConfigFile("teams_info_pool", temp_teams, self.domain, filename)
            Configurator.updateConfigFile("analysts_skills", temp_analysts, self.domain, filename)
            
            Variables.teams_info_pool = temp_teams
            Variables.analysts_skills = temp_analysts
            print("Analysts assigned successfully!")
            self.close()
            
    # Gets the days off picked
    def getPickedDaysOff(self, days_off_combo):
          
        days = []
        for i in range(days_off_combo.count()):
            if days_off_combo.item_checked(i):
                days.append(days_off_combo.itemText(i))
        return days
    
    # Puts the days off into a string
    def daysOffOutput(self, days):
        
        days_off = ""
        for i in range(len(days)):
            if len(days) > 1:
                if i == len(days) - 1:
                    days_off += " and "
                else:
                    if days_off != "":
                        days_off += ", "
            days_off += days[i]
        
        if days_off == "":
            days_off = "---"
            
        return days_off
    
    # Puts the days off into a list
    def getPickedDaysList(self, picked_daysoff):
        
        days_off = []
        for i in range(self.analyst_day_off_combobox.count()):
            #print(self.analyst_day_off_combobox.itemText(i))
            if self.analyst_day_off_combobox.itemText(i) in picked_daysoff:
                days_off.append(self.analyst_day_off_combobox.itemText(i))
                    
        return days_off     
            
    # Returns the index of an incident
    def getIncidentIndex(self, name):
        
        for i in Variables.incident_area[self.domain].keys():
            if Variables.incident_area[self.domain][i]['type'] == name:
                return i
            
    # Returns the probability of all incidents
    def getIncidentsProb(self):
        
        incidents_prob = 0
        for incident in self.incidents[self.domain].keys():
            incidents_prob += float(self.incidents[self.domain][incident]['widget prob'].text())
            
        return incidents_prob
           
    # Changes the option of having all shifts occupied
    def shiftsMode(self, shift):
        
        if shift.isChecked():
            print("All shifts will have analysts")
            Variables.allshifts_occupied = True
            self.analyst_information.setText("Note: All teams should have at least three analysts!")
        else:
            print("There may be shifts with no analysts")
            Variables.allshifts_occupied = False
            self.analyst_information.setText("Note: All teams should have at least one analyst!")
    
    # Changes the option of having all shifts occupied
    def TeamsPrioritizationMode(self, teams):
        
        if teams.isChecked():
            print("Prioritize lower Teams (L1)")
            Variables.lower_teams = True
            self.teams_customizable.setEnabled(False)
            print("Temp", Variables.teams_frequency)

        else:
            print("No Prioritization is needed for the teams allocation")
            Variables.lower_teams = False
            self.teams_customizable.setEnabled(True)
            print("Temp", Variables.teams_frequency)
            
    # Sets the initial teams in the UI
    def initStandardTeams(self, main_layout):
        
        for team in Variables.teams_info_pool.keys():
            self.standard_teams[team] = {}
            self.standard_teams[team]['analysts'] = Variables.teams_info_pool[team]
            
            team_layout = QHBoxLayout()
            self.curr_team = QGroupBox("Team " + team, self)
            self.curr_team.setFont(self.features_font)
            self.curr_team.setLayout(team_layout)
            self.curr_team_analysts = QLabel(str("Analysts: " + (', '.join(Variables.teams_info_pool[team]))), self)
            self.standard_teams[team]['widget'] = self.curr_team
            
            team_layout.addWidget(self.curr_team_analysts)
            main_layout.addWidget(self.curr_team)
            
    # Locks the possibility of changing the probability of an incident
    def areaMode(self, checkbox_button, area, spinbox):
	
        if not checkbox_button.property("locked"):
            print("The probability of the " + area + " was locked")
            checkbox_button.setProperty("locked", True)
            checkbox_button.setStyle(checkbox_button.style())
            spinbox.setEnabled(False)
        else:
            print("The probability of the " + area + " was unlocked")
            spinbox.setEnabled(True)
            checkbox_button.setProperty("locked", False)
            checkbox_button.setStyle(checkbox_button.style())
        
    # Changes between standard and custom Teams
    def teamMode(self, mode, main_layout):
        
        if mode.text() == "Standard":
            if mode.isChecked():
                for team in self.standard_teams:
                    widget = self.standard_teams[team]['widget']
                    widget.setHidden(False)
                    self.add_analyst_button.setHidden(True)
                    self.analysts_input.setHidden(True)
                    self.teams_customizable.setHidden(True)
                    
                for team in self.custom_teams:
                    self.custom_teams[team]['groupbox widget'].setHidden(True)
                
                self.shifts.setHidden(True)
                self.team_allocation_type.setHidden(True)
                self.analyst_information.setHidden(True)
                self.save_team_config_button.setHidden(True)  
                self.load_teams_button.setHidden(True)  
        if mode.text() == "Custom":
            if mode.isChecked():
                for team in self.standard_teams:
                    widget = self.standard_teams[team]['widget']
                    widget.setHidden(True)
                    self.add_analyst_button.setHidden(False)
                    self.analysts_input.setHidden(False)
                    self.teams_customizable.setHidden(False)
                    
                for team in self.custom_teams:
                    self.custom_teams[team]['groupbox widget'].setHidden(False)
                    
                self.shifts.setHidden(False)
                self.team_allocation_type.setHidden(False)
                self.analyst_information.setHidden(False)
                self.save_team_config_button.setHidden(False)  
                self.load_teams_button.setHidden(False)  
                     
    # Closes the subwindow
    def closeEvent(self, event):
        if self.isActiveWindow():
            self.parent_windows.subwindows.remove(self)
        self.close()