# -*- coding: utf-8 -*-
"""
Created on Thu Apr 02 08:05:51 2015

@author: speechlab
"""
from __future__ import division
import numpy as np
from quatUtils import QuatUtils as q
import os
import glob

class BiteplateUtils():
    
    def __init__(self, parent = None):
        super(BiteplateUtils,self).__init__(parent)
        
    @staticmethod
    def processAllFiles(bpfile, indir, osCol, msCol, outdir, decPrec):
        files = glob.glob(indir+'/*.tsv')
        OS, rot = BiteplateUtils.getRotation(bpfile, osCol, msCol)
        for f in files:
            data, header = BiteplateUtils.correctData(f, OS, rot)
            BiteplateUtils.writetsv(data, header, f, outdir, decPrec)
        
    @staticmethod
    def correctData(fileToCorrect, OS, rot):
        
        offset = np.array([-4,-1, 0])
        rawdat, header = BiteplateUtils.loadTsv(fileToCorrect)
        
        numSensors = int(np.floor(rawdat.shape[1]/9))
        swapDat= rawdat.copy()
        for j in range(1,numSensors-1):
            #Position values swapped
            swapDat[:,5+9*j] = rawdat[:,6+9*j]
            swapDat[:,6+9*j] = rawdat[:,5+9*j]
            swapDat[:,7+9*j] = -rawdat[:,7+9*j]
             
            #Quaternion values swapped
            swapDat[:,9+9*j] = rawdat[:,10+9*j]
            swapDat[:,10+9*j] = rawdat[:,9+9*j]
            swapDat[:,12+9*j] = -rawdat[:,11+9*j]
            
        BPCorrect = swapDat
            
        for j in range(1,numSensors-1): 
            BPCorrect[:,5+9*j:8+9*j] = q.qvqc(rot,(swapDat[:,5+9*j:8+9*j]-OS))-offset
            BPCorrect[:,8+9*j:12+9*j] = q.correctQuat(swapDat[:,8+9*j:12*9+j], rot)
            BPCorrect[:,3+9*j] = j
        
        return BPCorrect, header
                    #To complete:  Write a BPCFolder method that calls all of these functions to correct the contents of an entire folder.
                #  Also, start by writing a writetsv method that makes the output data look less crappy, (copy dr. j's writetsv in matlab)
        #PROBLEM IN OLD MATLAB WRITE TSV>>  FFIRST IS WRITE %6.F INSTEAD OF %.6F  that's why the number comes out as an integer.. doh.

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
        os = rawdat[:,(osCol-1):(osCol+2)]
        ms = rawdat[:,(msCol-1):(msCol+2)]

        #Rearrange the columns
        os = np.column_stack((os[:,1],os[:,0],-os[:,2]))
        ms = np.column_stack((ms[:,1],ms[:,0],-ms[:,2]))
        
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
        
if(__name__ == '__main__'):

    bpfile =  "05_ENGL_F_biteplate_2.tsv"
    kinfile = "05_ENGL_F_words5.tsv"
    outdir = 'C:/python_workspace/BPCTool/Output Folder'
    indir = 'C:/python_workspace/BPCTool/Input Folder'
    osCol = 87
    msCol = 96
    BiteplateUtils.processAllFiles(bpfile, indir, osCol, msCol, outdir, 4)
        