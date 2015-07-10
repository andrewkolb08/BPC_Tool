# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 14:18:53 2015

@author: Andrew
"""

from __future__ import division
import sys
import bpInput
import bpUtils
from PyQt4 import QtCore, QtGui
import glob
import time

__version__ = "1.0.0"


class MainWindow(QtGui.QDialog):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        flags = QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        #Find a way to have a minimize button here?
        #Just did, bro.  see the setWindowFlags above
        self.completed = 0
        self.bpDlg = bpInput.BiteplateInput()
        self.img = QtGui.QLabel('<b> Instructions </b>')
        self.correctButton = QtGui.QPushButton('Correct All')
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0,100)
        self.progressLabel = QtGui.QLabel('Idle')
        
        topLayout = QtGui.QHBoxLayout()
        topLayout.addWidget(self.img)
        topLayout.addWidget(self.bpDlg)
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.progressLabel)
        bottomLayout.addWidget(self.progressBar)
        bottomLayout.addWidget(self.correctButton)
        
        finalLayout = QtGui.QVBoxLayout()
        finalLayout.addLayout(topLayout)
        finalLayout.addLayout(bottomLayout)
        
        #Create a status label that gets updated with a qstatus bar on each iteration.. Also!
        #Disable the correct button when we are correcting, and reimplement the close event so
        #The user doesn't crap it up by exiting during correction.  Maybe add a cancel button
        #then if they thought there was a mistake of some kind?
        
        self.setLayout(finalLayout)
        
        self.connect(self.correctButton, QtCore.SIGNAL('clicked()'), self.correctAll)
        
    def correctAll(self):
        userInput = self.bpDlg.sendData()
        if(userInput is not None):
            self.processAllFiles(userInput[0],userInput[1],
                                                   userInput[2],userInput[3],
                                                   userInput[4],userInput[5])
                   
    def processAllFiles(self,bpfile, osNum, msNum, indir, outdir, decPrec):
        osCol = 5+(osNum-1)*9
        msCol = 5+(msNum-1)*9        
        
        self.correctButton.setEnabled(False)
        self.progressLabel.setText('Initializing...')
        self.progressBar.setValue(1)
        files = glob.glob(indir+'/*.tsv')
        OS, rot = bpUtils.BiteplateUtils.getRotation(bpfile, osCol, msCol)
        self.progressBar.setValue(2)
        self.numFiles = len(files)
        self.thread = QtCore.QThread()
        self.worker = Worker(OS, rot, indir, outdir, decPrec, files)
        
        self.worker.moveToThread(self.thread)
#        self.thread.connect(QtCore.SIGNAL('started()'), self.worker.processFiles())                
        self.thread.started.connect(self.worker.processFiles)
        self.connect(self.worker, QtCore.SIGNAL('finishedOne()'), self.updateProgress)
        self.connect(self.worker, QtCore.SIGNAL('finishedAll()'), self.resetProgress)
        self.thread.start()
        self.progressLabel.setText('Beginning file 1 of %i' % self.numFiles)

        
    def updateProgress(self):
        self.completed+= 1
        self.progressLabel.setText('Completed %i of %i files' % (self.completed, self.numFiles))
        self.progressBar.setValue(round((self.completed/self.numFiles)*100))
        time.sleep(1)
        
        
    def resetProgress(self):
        self.thread.terminate()
        self.worker = None
        QtGui.QMessageBox.information(self,'Complete', 'All files have been corrected.')
        self.progressLabel.setText('Idle')
        self.progressBar.setValue(0)
        self.completed = 0
        self.numFiles = 0
        self.correctButton.setEnabled(True)
        #38 seconds total
        
    def closeEvent(self, event):
        if not self.correctButton.isEnabled():
            quit_msg = "Correction in progress.  Are you sure you want to exit the program?"
            reply = QtGui.QMessageBox.question(self, 'Message', 
                     quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                self.thread.terminate()
                event.accept()
            else:
                event.ignore()
                
        
class Worker(QtCore.QObject):   
    
    def __init__(self, OS, rot, indir, outdir, decPrec, files, parent = None):
        super(Worker, self).__init__(parent)
        self.OS = OS
        self.rot = rot
        self.indir = indir
        self.outdir = outdir
        self.decPrec = decPrec
        self.files = files
        
    @QtCore.pyqtSlot()
    def processFiles(self):
        for f in self.files:
            data, header = bpUtils.BiteplateUtils.correctData(f, self.OS, self.rot)
            bpUtils.BiteplateUtils.writetsv(data, header, f, self.outdir, self.decPrec)
            self.emit(QtCore.SIGNAL("finishedOne()"))
            
        self.emit(QtCore.SIGNAL("finishedAll()"))
        
        
def main():
    """
        Just sets up the application and runs it!
    """
    qApp = QtGui.QApplication(sys.argv)
    qApp.setApplicationName("BPC Tool")
    qApp.setOrganizationName("Marquette University Speechlab")
#    qApp.setWindowIcon(QtGui.QIcon(":/vtIcon.ico"))
    form = MainWindow()
    form.show()
    sys.exit(qApp.exec_())


main()