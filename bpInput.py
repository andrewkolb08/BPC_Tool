# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 13:46:32 2015

@author: AJK
"""

from PyQt4 import QtCore, QtGui
import os
import sys

class BiteplateInput(QtGui.QWidget):
    
    def __init__(self, parent = None):
        super(BiteplateInput,self).__init__(parent)
        
        self.currentFile  = None
        bpInfoLabel = QtGui.QLabel('<b>Biteplate File Information</b>')
        inputInfoLabel = QtGui.QLabel('<b>Input File Information</b>')
        outputInfoLabel = QtGui.QLabel('<b>Output File Information</b>')
        resampInfoLabel = QtGui.QLabel('<b>Resampling Information</b>')
        bpLocationLabel = QtGui.QLabel('Biteplate File: ')
        osLabel = QtGui.QLabel('OS Sensor Number: ')
        msLabel = QtGui.QLabel('MS Sensor Number: ')
        sourceLabel = QtGui.QLabel('Input Folder: ')
        decimalLabel = QtGui.QLabel('Decimal Precision: ')
        sinkLabel = QtGui.QLabel('Output Folder: ')
        resampLabel = QtGui.QLabel('Resample Data: ')
        freqLabel = QtGui.QLabel('Desired Frequency: ')
        freqUnits = QtGui.QLabel('Hz')
        
        self.decimalBox = QtGui.QSpinBox()
        self.decimalBox.setRange(3,9)
        self.decimalBox.setValue(4)
        
        
        self.bpFileEdit = QtGui.QLineEdit('')
        self.inputEdit = QtGui.QLineEdit('')
        self.outputEdit = QtGui.QLineEdit('')
        # self.bpFileEdit.setReadOnly(True)
        # self.inputEdit.setReadOnly(True)
        # self.outputEdit.setReadOnly(True)        
        
        self.osBox = QtGui.QSpinBox()
        self.osBox.setRange(1,16)
        self.osBox.setValue(10)
        self.msBox = QtGui.QSpinBox()
        self.msBox.setRange(1,16)
        self.msBox.setValue(11)
        
        self.resampBox = QtGui.QCheckBox('')
        self.resampBox.setCheckState(2)
        self.freq = QtGui.QSpinBox()
        self.freq.setRange(0,1000)
        self.freq.setValue(400)
        
        bpFileBrowseButton = QtGui.QPushButton('Browse...')
        sourceBrowseButton = QtGui.QPushButton('Browse...')
        sinkBrowseButton = QtGui.QPushButton('Browse...')
        
        layout = QtGui.QGridLayout()
        layout.addWidget(bpInfoLabel,0,1,1,2)
        layout.addWidget(bpLocationLabel, 1,0,1,1)
        layout.addWidget(self.bpFileEdit,1,1,1,4)
        layout.addWidget(bpFileBrowseButton,1,5,1,1)
        layout.addWidget(osLabel,2,1,1,1)
        layout.addWidget(self.osBox,2,2,1,1)
        layout.addWidget(msLabel,2,3,1,1)
        layout.addWidget(self.msBox,2,4,1,1)
        layout.addWidget(inputInfoLabel,3,1,1,2)
        layout.addWidget(sourceLabel,4,0,1,1)
        layout.addWidget(self.inputEdit,4,1,1,4)
        layout.addWidget(sourceBrowseButton,4,5,1,1)
        layout.addWidget(outputInfoLabel, 5,1,1,2)
        layout.addWidget(sinkLabel,6,0,1,1)
        layout.addWidget(self.outputEdit,6,1,1,4)
        layout.addWidget(sinkBrowseButton,6,5,1,1)
        layout.addWidget(decimalLabel,7,1,1,1)
        layout.addWidget(self.decimalBox,7,2,1,1)
        layout.addWidget(resampInfoLabel,8,1,1,2)
        layout.addWidget(resampLabel,9,1)
        layout.addWidget(self.resampBox,9,2,1,1)
        layout.addWidget(freqLabel,9,3,1,4)
        layout.addWidget(self.freq,9,4)
        layout.addWidget(freqUnits,9,5)
        self.setLayout(layout)
        
        self.sourceBrowseCallback = lambda who="source": self.selectDir(who)
        self.connect(sourceBrowseButton,QtCore.SIGNAL("clicked()"),self.sourceBrowseCallback)
        
        self.sinkBrowseCallback = lambda who="sink": self.selectDir(who)
        self.connect(sinkBrowseButton,QtCore.SIGNAL("clicked()"),self.sinkBrowseCallback)
        self.connect(bpFileBrowseButton,QtCore.SIGNAL("clicked()"),self.selectBPFile)
        
        
    def selectDir(self,who):
        dir = os.path.dirname(unicode(self.currentFile))\
        if self.currentFile is not None else "."
        dirToSaveIn = QtCore.QString(QtGui.QFileDialog.getExistingDirectory(self,
                            "Biteplate Correction Tool - Choose Folder", dir,
                            QtGui.QFileDialog.ShowDirsOnly))                    
        if dirToSaveIn is not QtCore.QString():
            if who is 'sink':
                self.outputEdit.setText(dirToSaveIn)
            elif who is 'source':
                self.inputEdit.setText(dirToSaveIn)
        self.currentFile = str(dirToSaveIn)
             
    def selectBPFile(self):
        dir = os.path.dirname(unicode(self.currentFile)) \
                if self.currentFile is not None else "."
        bpfile = QtCore.QString(QtGui.QFileDialog.getOpenFileName(self,
                            "Biteplate Correction Tool - Choose Biteplate File", dir,
                            "TSV files (*.tsv)"))
        if(bpfile == QtCore.QString()):
            return
        else:
            self.bpFileEdit.setText(bpfile)
        self.currentFile = os.path.dirname(str(bpfile))
            
    def validateInput(self, data):
        if '' in data:
            QtGui.QMessageBox.warning(self,'Invalid Input', 'No fields can be left empty')
            return False
            
        elif data[1] == data[2]:
            QtGui.QMessageBox.warning(self, 'Invalid Input', 'OS and MS sensors must be different numbers')
            return False
        else:
            return True
    
    def sendData(self):
        bpfile = unicode(self.bpFileEdit.text()).strip()
        osCol = self.osBox.value()
        msCol = self.msBox.value()
        indir = unicode(self.inputEdit.text()).strip()
        outdir = unicode(self.outputEdit.text()).strip()
        decimal = self.decimalBox.value()
        resamp = self.resampBox.isChecked()
        freq = self.freq.value()
        toReturn = (bpfile, int(osCol), int(msCol), indir, outdir, int(decimal), resamp, int(freq))
        okay = self.validateInput(toReturn)
        
        if(okay):
            return toReturn
        else:
            return None
        
if __name__ == '__main__':
    qtApp = QtGui.QApplication(sys.argv)
    form = BiteplateInput()
    form.show()
    sys.exit(qtApp.exec_())