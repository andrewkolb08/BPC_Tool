import bpInput
import bpUtils
import os
import numpy as np
import glob
import tkinter as tk
import tkFileDialog

def main():
    root = tk.Tk()
    root.withdraw()
    rootDir = tkFileDialog.askdirectory() + '\\'
    bpDir = '\\Calibration\\BitePlate\\'
    rawDir = '\\Kinematic\\Raw\\'
    corDir = '\\Kinematic\\Corrected\\'
    folds = os.listdir(rootDir)
    num = '0', '1', '2', '3', '4', '5'
    osCol = 86
    msCol = 95
    decPrec = 4
    #folds = folds[:1]
    
    for f in folds:
        if f.startswith(num):
            subFold = rootDir + f + bpDir
            bpfiles = [fn for fn in glob.glob(subFold+'/*biteplate*.tsv') if "_BPC" not in fn]
            bpfile = bpfiles[-1]
            indir = rootDir + f + rawDir
            outdir = rootDir + f + corDir
            files = glob.glob(indir+'/*.tsv')
            OS, rot = bpUtils.BiteplateUtils.getRotation(bpfile, osCol, msCol)
            processFiles(OS, rot, indir, outdir, decPrec, files)
            print f + " done."
            
def processFiles(OS, rot, indir, outdir, decPrec, files):
        for f in files:
            data, header = bpUtils.BiteplateUtils.correctData(f, OS, rot)
            bpUtils.BiteplateUtils.writetsv(data, header, f, outdir, decPrec)
            
main()
