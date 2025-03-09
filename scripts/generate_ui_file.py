#!/usr/bin/env python
"""
Generate UI File Script

This script creates a Qt Designer UI file for the Prometheus Prompt Generator
main window based on the current hand-coded UI.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QTextEdit, QListWidget,
    QAbstractItemView, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from prometheus_prompt_generator.utils.constants import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE
except ImportError:
    DEFAULT_FONT_FAMILY = "Segoe UI"
    DEFAULT_FONT_SIZE = 10

def generate_ui_file():
    """Generate a Qt Designer UI file for the main window."""
    ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                         'prometheus_prompt_generator', 'ui', 'designer')
    
    # Create the ui directory if it doesn't exist
    os.makedirs(ui_dir, exist_ok=True)
    
    ui_file_path = os.path.join(ui_dir, 'main_window.ui')
    
    # Basic UI XML structure
    ui_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>700</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Prometheus AI Prompt Generator</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <widget class="QSplitter" name="splitter">
      <property name="orientation">
       <enum>Qt::Horizontal</enum>
      </property>
      <widget class="QWidget" name="leftWidget" native="true">
       <layout class="QVBoxLayout" name="leftLayout">
        <item>
         <widget class="QLabel" name="promptTypesHeader">
          <property name="font">
           <font>
            <family>{DEFAULT_FONT_FAMILY}</family>
            <pointsize>{DEFAULT_FONT_SIZE + 2}</pointsize>
            <weight>75</weight>
            <bold>true</bold>
           </font>
          </property>
          <property name="text">
           <string>Prompt Types</string>
          </property>
         </widget>
        </item>
        <item>
         <layout class="QHBoxLayout" name="searchLayout">
          <item>
           <widget class="QLineEdit" name="searchInput">
            <property name="placeholderText">
             <string>Search prompts...</string>
            </property>
           </widget>
          </item>
         </layout>
        </item>
        <item>
         <layout class="QHBoxLayout" name="selectButtonsLayout">
          <item>
           <widget class="QPushButton" name="selectAllButton">
            <property name="text">
             <string>Select All</string>
            </property>
           </widget>
          </item>
          <item>
           <widget class="QPushButton" name="selectNoneButton">
            <property name="text">
             <string>Select None</string>
            </property>
           </widget>
          </item>
         </layout>
        </item>
        <item>
         <widget class="QListWidget" name="promptList">
          <property name="alternatingRowColors">
           <bool>true</bool>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QPushButton" name="addPromptButton">
          <property name="text">
           <string>Add Custom Prompt</string>
          </property>
         </widget>
        </item>
       </layout>
      </widget>
      <widget class="QWidget" name="rightWidget" native="true">
       <layout class="QVBoxLayout" name="rightLayout">
        <item>
         <widget class="QLabel" name="urgencyHeader">
          <property name="font">
           <font>
            <family>{DEFAULT_FONT_FAMILY}</family>
            <pointsize>{DEFAULT_FONT_SIZE + 2}</pointsize>
            <weight>75</weight>
            <bold>true</bold>
           </font>
          </property>
          <property name="text">
           <string>Urgency Level</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QLabel" name="urgencyDisplay">
          <property name="font">
           <font>
            <family>{DEFAULT_FONT_FAMILY}</family>
            <pointsize>{DEFAULT_FONT_SIZE}</pointsize>
            <weight>75</weight>
            <bold>true</bold>
           </font>
          </property>
          <property name="text">
           <string>Normal (5/10)</string>
          </property>
          <property name="alignment">
           <set>Qt::AlignCenter</set>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QSlider" name="urgencySlider">
          <property name="minimum">
           <number>1</number>
          </property>
          <property name="maximum">
           <number>10</number>
          </property>
          <property name="value">
           <number>5</number>
          </property>
          <property name="orientation">
           <enum>Qt::Horizontal</enum>
          </property>
          <property name="tickPosition">
           <enum>QSlider::TicksBelow</enum>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QLabel" name="generatedPromptHeader">
          <property name="font">
           <font>
            <family>{DEFAULT_FONT_FAMILY}</family>
            <pointsize>{DEFAULT_FONT_SIZE + 2}</pointsize>
            <weight>75</weight>
            <bold>true</bold>
           </font>
          </property>
          <property name="text">
           <string>Generated Prompt</string>
          </property>
         </widget>
        </item>
        <item>
         <widget class="QTextEdit" name="outputText">
          <property name="placeholderText">
           <string>Generated prompt will appear here. You can edit it as needed.</string>
          </property>
         </widget>
        </item>
        <item>
         <layout class="QHBoxLayout" name="buttonRow">
          <item>
           <widget class="QPushButton" name="generatePromptsButton">
            <property name="minimumHeight">
             <number>40</number>
            </property>
            <property name="text">
             <string>Generate Prompts</string>
            </property>
           </widget>
          </item>
          <item>
           <widget class="QPushButton" name="copyToClipboardButton">
            <property name="minimumHeight">
             <number>40</number>
            </property>
            <property name="text">
             <string>Copy to Clipboard</string>
            </property>
           </widget>
          </item>
         </layout>
        </item>
       </layout>
      </widget>
     </widget>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1000</width>
     <height>22</height>
    </rect>
   </property>
   <widget class="QMenu" name="menuFile">
    <property name="title">
     <string>File</string>
    </property>
    <addaction name="actionImport"/>
    <addaction name="actionExport"/>
    <addaction name="separator"/>
    <addaction name="actionExit"/>
   </widget>
   <widget class="QMenu" name="menuEdit">
    <property name="title">
     <string>Edit</string>
    </property>
    <addaction name="actionChangeFont"/>
    <addaction name="actionResetFont"/>
   </widget>
   <widget class="QMenu" name="menuView">
    <property name="title">
     <string>View</string>
    </property>
    <widget class="QMenu" name="menuTheme">
     <property name="title">
      <string>Theme</string>
     </property>
     <addaction name="actionLightTheme"/>
     <addaction name="actionDarkTheme"/>
    </widget>
    <addaction name="menuTheme"/>
   </widget>
   <widget class="QMenu" name="menuHelp">
    <property name="title">
     <string>Help</string>
    </property>
    <addaction name="actionAbout"/>
   </widget>
   <addaction name="menuFile"/>
   <addaction name="menuEdit"/>
   <addaction name="menuView"/>
   <addaction name="menuHelp"/>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <action name="actionImport">
   <property name="text">
    <string>Import Prompts...</string>
   </property>
  </action>
  <action name="actionExport">
   <property name="text">
    <string>Export Prompts...</string>
   </property>
  </action>
  <action name="actionExit">
   <property name="text">
    <string>Exit</string>
   </property>
  </action>
  <action name="actionChangeFont">
   <property name="text">
    <string>Change Font...</string>
   </property>
  </action>
  <action name="actionResetFont">
   <property name="text">
    <string>Reset Font</string>
   </property>
  </action>
  <action name="actionLightTheme">
   <property name="text">
    <string>Light</string>
   </property>
  </action>
  <action name="actionDarkTheme">
   <property name="text">
    <string>Dark</string>
   </property>
  </action>
  <action name="actionAbout">
   <property name="text">
    <string>About</string>
   </property>
  </action>
 </widget>
 <resources/>
 <connections/>
</ui>
'''
    
    # Write the UI file
    with open(ui_file_path, 'w', encoding='utf-8') as f:
        f.write(ui_xml)
    
    print(f"UI file generated at: {ui_file_path}")
    return ui_file_path

if __name__ == "__main__":
    generate_ui_file() 