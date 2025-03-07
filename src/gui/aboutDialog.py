#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTabWidget, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

class Ui_aboutDialog(object):
    """UI for the About dialog"""
    
    def setupUi(self, aboutDialog):
        """Setup UI elements"""
        aboutDialog.setObjectName("aboutDialog")
        aboutDialog.resize(500, 400)
        aboutDialog.setWindowTitle("About CreepyAI")
        
        # Main layout
        self.mainLayout = QVBoxLayout(aboutDialog)
        self.mainLayout.setObjectName("mainLayout")
        
        # Logo and version
        self.logoLabel = QLabel(aboutDialog)
        self.logoLabel.setPixmap(QPixmap(":/creepy/logo"))
        self.logoLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.logoLabel)
        
        self.versionLabel = QLabel("Version 1.1", aboutDialog)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.versionLabel)
        
        # Tab widget for About, License, Credits
        self.tabWidget = QTabWidget(aboutDialog)
        
        # About tab
        self.aboutTab = QWidget()
        self.aboutTabLayout = QVBoxLayout(self.aboutTab)
        
        self.aboutText = QTextBrowser(self.aboutTab)
        self.aboutText.setOpenExternalLinks(True)
        self.aboutText.setHtml("""
        <h2>CreepyAI</h2>
        <p>CreepyAI is a geolocation intelligence tool that collects, analyzes, and visualizes geolocation data from various sources.</p>
        <p>It is designed as a research tool for open source intelligence investigations.</p>
        <p>Website: <a href="https://geocreepy.com">geocreepy.com</a></p>
        """)
        self.aboutTabLayout.addWidget(self.aboutText)
        
        self.tabWidget.addTab(self.aboutTab, "About")
        
        # License tab
        self.licenseTab = QWidget()
        self.licenseTabLayout = QVBoxLayout(self.licenseTab)
        
        self.licenseText = QTextBrowser(self.licenseTab)
        self.licenseText.setPlainText("""
MIT License

Copyright (c) 2023 CreepyAI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
        """)
        self.licenseTabLayout.addWidget(self.licenseText)
        
        self.tabWidget.addTab(self.licenseTab, "License")
        
        # Credits tab
        self.creditsTab = QWidget()
        self.creditsTabLayout = QVBoxLayout(self.creditsTab)
        
        self.creditsText = QTextBrowser(self.creditsTab)
        self.creditsText.setHtml("""
        <h3>Credits</h3>
        <p>CreepyAI uses the following open source libraries:</p>
        <ul>
            <li>PyQt5 - Qt for Python</li>
            <li>Leaflet.js</li>
            <li>Yapsy</li>
            <li>ConfigObj</li>
        </ul>
        <p>Special thanks to all contributors and users!</p>
        """)
        self.creditsTabLayout.addWidget(self.creditsText)
        
        self.tabWidget.addTab(self.creditsTab, "Credits")
        
        self.mainLayout.addWidget(self.tabWidget)
        
        # Close button
        self.closeButton = QPushButton("Close", aboutDialog)
        self.closeButton.setDefault(True)
        self.closeButton.clicked.connect(aboutDialog.accept)
        self.mainLayout.addWidget(self.closeButton)
