# -*- coding: utf-8 -*-
"""
Created on Thu Apr 02 08:05:51 2015

@author: speechlab
"""
from __future__ import division
import numpy as np
from quatUtils import QuatUtils as q
import os

class BiteplateUtils():
    
    def __init__(self, parent = None):
        pass
    
    @staticmethod
    def correctData(fileToCorrect, OS, rot, resamp, freq):
        
        offset = np.array([-4,-1, 0])
        rawdat, header = BiteplateUtils.loadTsv(fileToCorrect)
        
        numSensors = int(np.floor((rawdat.shape[1]-3)/9))
        swapDat = rawdat.copy()
        BPCorrect = swapDat
            
        for j in range(1,numSensors): 
            BPCorrect[:,5+9*j:8+9*j] = q.qvqc(rot,(swapDat[:,5+9*j:8+9*j]-OS))-offset
            BPCorrect[:,8+9*j:12+9*j] = q.correctQuat(swapDat[:,8+9*j:12+9*j], rot)
            BPCorrect[:,3+9*j] = j
        
        if resamp:
            BPCorrect = BiteplateUtils.resample(BPCorrect, freq)
        
        return BPCorrect, header

    @staticmethod
    def writetsv(data, header, infile, outdir, numDec):
        
        numDec = str(numDec)
        fname = os.path.split(infile)
        name, ext = os.path.splitext(fname[1])
        bpcName = os.path.join(outdir,name+'_BPC'+ext)
        outHeader = '\t'.join(header)
        numSensors = np.floor(data.shape[1]/9)
        finit='%.4f\t%g\t%g\t';  #first 3 columns format string
        ffirst='%g\t%g\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t' # first sensor
        frep='%g\t%g\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t'    # each sensor
        flast='%g\t%g\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f\t%.'+numDec+'f'   #last sensor

        frmt = finit+ffirst+frep*(numSensors-2)+flast
        np.set_printoptions(nanstr = '\t')
        np.savetxt(bpcName, data, fmt = frmt, delimiter = '\t', header=outHeader)
        
    @staticmethod
    def getRotation(bpfile,osCol, msCol):
        rawdat, header = BiteplateUtils.loadTsv(bpfile)
        os = rawdat[:,(osCol):(osCol+3)]
        ms = rawdat[:,(msCol):(msCol+3)]

        #We don't rearrange the columns anymore.
        #os = np.column_stack((os[:,1],os[:,0],-os[:,2]))
        #ms = np.column_stack((ms[:,1],ms[:,0],-ms[:,2]))
        
        MS = np.nanmean(ms,axis=0)
        OS = np.nanmean(os,axis=0)
        REF = np.array([0,0,0])
        
        ref_t = REF-OS
        ms_t = MS-OS
        z = np.cross(ms_t,ref_t)
        z = z/np.linalg.norm(z)
        y = np.cross(z,ms_t)
        y = y/np.linalg.norm(z)

        l1 = np.dot(y,ref_t)/np.linalg.norm(y)
        l2 = np.linalg.norm(ms_t)
        ref_tnew = np.array([0, abs(l1), 0])
        ms_tnew = np.array([-1*abs(l2), 0, 0])
        ref_ty = y*abs(l1)/np.linalg.norm(y)
        
        x1 = ms_t
        x2 = ms_tnew
        y1 = ref_ty
        y2 = ref_tnew
        
        
        norm1 = np.cross(x1,x2)
        norm1 = norm1/np.linalg.norm(norm1)
        norm2 = np.cross(y1,y2)
        norm2 = norm2/np.linalg.norm(norm2)
        f1 = np.cross(norm1,(x1+x2)/2)
        f1 = f1/np.linalg.norm(f1)
        f2 = np.cross(norm2, (y1+y2)/2)
        f2 = f2/np.linalg.norm(f2)
        axis = np.cross(f1,f2)
        axis = axis/np.linalg.norm(axis)
        
        r = np.linalg.norm(x1)*np.sin(np.arccos((np.dot(x1,axis))/(np.linalg.norm(x1)*np.linalg.norm(axis))))
        theta = np.arcsin((np.sqrt((x1[0]-x2[0])**2+(x1[1]-x2[1])**2+(x1[2]-x2[2])**2)/(2*r)))
          
        
        if(theta>(np.pi/2)):
            theta = np.pi-theta
            
        q0 = np.cos(theta);
        qx = np.sin(theta)*axis[0]
        qy = np.sin(theta)*axis[1]
        qz = np.sin(theta)*axis[2]
        
        qout = np.array([q0,qx,qy,qz])
        #Check your work!
        ms_new2 = q.qcvq(qout,(MS-OS))
        if((ms_new2[0,1]<0.000001) and (ms_new2[0,2]<0.000001)):
            qout = q.qconj(qout)
        
        return OS, qout
        
    @staticmethod
    def loadTsv(kinfilename):
        """
            Loads the tsv file, making A LOT of assumptions about the data.
            If this tool is to work with many different data sets, this will have
            to become safer (use some try, catch blocks) and the data will be 
            different each time.
        """
        data = np.genfromtxt(unicode(kinfilename), skip_header=1, delimiter = '\t')
        header = np.genfromtxt(unicode(kinfilename),skip_footer=np.shape(data)[0],delimiter = '\t', dtype = object)
        return data, header

    @staticmethod
    def saveRot(OS, rot, infile):
        """
            Saves the OS and rotation values (calculated in bpUtils.BiteplateUtils.getRotation) to .txt files 
			in the same directory as the biteplate file.  
			Filenames will be in the form of [subj]_biteplate_OS.txt and [subj]_biteplate_Rotation.txt
        """
        fname = os.path.split(infile)
        name, ext = os.path.splitext(fname[1])
        outdir = os.path.dirname(infile)
        osName = os.path.join(outdir,name+'_OS.txt')
        rotName = os.path.join(outdir,name+'_Rotation.txt')
        np.savetxt(osName, OS, delimiter = '\t')
        np.savetxt(rotName, rot, delimiter = '\t')
        # nothing returned
        
    @staticmethod
    def resample(rawdat, freq):
        # The columns containing whole-number data ('MeasId', 'WavId', 'Sensor # Id', 'Sensor # Status', etc.)
        rnd = [1,2,3,4,12,13,21,22,30,31,39,40,48,49,57,58]
        
        
        # Checks for "error rows" at the beginning of the file.
        # Error rows will have time values in the hundreds of thousands of seconds
        row = 0
        while rawdat[row,0] > 10:
            row = row + 1
        
        rawdat = rawdat[row:,:]
        
        
        # Generates a sequence from the first to last sample times evenly spaced at the frequency given
        x = np.arange(rawdat[0,0], rawdat[-1,0], (1.0/freq))
        
        
        # An empty array which will later hold the new, interpolated values.
        # Note: np.empty generates an array filled with very tiny (on the order of e-292),
        # but still non-zero values. To ensure that the random values aren't potentially
        # mistaken as actual data, all values are set to 'nan' (a.k.a. 'NA').
        newdat = np.empty([len(x), len(rawdat[0])]) * np.nan
        
        
        # Performs a linear interpolation on each column
        for i in range(len(rawdat[0])):
            newdat[:,i] = np.interp(x, rawdat[:,0], rawdat[:,i])
        
        
        # Rounds the previously mentioned whole-number columns back to whole numbers, mainly for aesthetics
        for r in rnd:
            newdat[:,r] = np.round(newdat[:,r], 0)

        
        # Returns the resampled data
        return newdat
    
if(__name__ == '__main__'):

    bpfile =  "01_MANB_F_biteplate.tsv"
    kinfile = "05_ENGL_F_words5.tsv"
    outdir = 'C:/python_workspace/BPCTool/Output Folder'
    indir = 'C:/python_workspace/BPCTool/Input Folder'
    osCol = 86
    msCol = 95
    OS, rot = BiteplateUtils.getRotation(bpfile, osCol, msCol)
    data, header = BiteplateUtils.correctData(kinfile, OS, rot)
    BiteplateUtils.writetsv(data, header, kinfile, outdir, 4)
        
