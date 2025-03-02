#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from ui.VerifyDeleteDialogUI import Ui_VerifyDeleteDialog

class VerifyDeleteDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_VerifyDeleteDialog()
        self.ui.setupUi(self)
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
