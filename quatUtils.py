# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 12:09:12 2015

@author: Andrew Kolb
"""
from __future__ import division

import numpy as np

class QuatUtils():    
    def __init__(self, parent = None):
        super(QuatUtils, self).__init__(parent)
       
    @staticmethod
    def qmult(q1,q2):
        numq1 = np.shape(np.matrix(q1))[0]
        numq2 = np.shape(np.matrix(q2))[0]
        
        if (numq1 != numq2):
            if( numq1 == 1):
                q1 = np.tile(q1,(numq2,1))
            else:
                q2 = np.tile(q2,(numq1,1))

        else:       #Both are 1
            q1 = np.matrix(q1)
            q2 = np.matrix(q2)
            
        prod1 = np.array([np.multiply(-q1[:,1],q2[:,1]), np.multiply(q1[:,1],q2[:,0]), np.multiply(-q1[:,1],q2[:,3]), np.multiply(q1[:,1],q2[:,2]) ])
        prod2 = np.array([np.multiply(-q1[:,2],q2[:,2]), np.multiply(q1[:,2],q2[:,3]), np.multiply(q1[:,2],q2[:,0]), np.multiply(-q1[:,2],q2[:,1]) ])
        prod3 = np.array([np.multiply(-q1[:,3],q2[:,3]), np.multiply(-q1[:,3],q2[:,2]), np.multiply(q1[:,3],q2[:,1]), np.multiply(q1[:,3],q2[:,0]) ])
        prod4 = np.array([np.multiply(q1[:,0],q2[:,0]),  np.multiply(q1[:,0],q2[:,1]), np.multiply(q1[:,0],q2[:,2]), np.multiply(q1[:,0],q2[:,3]) ])
        
        qout = prod1+prod2+prod3+prod4
        qout[qout == -0.] = 0
        return np.transpose(np.squeeze(qout))
        
    @staticmethod
    def qconj(qin):
        qin = np.matrix(qin)
        qout = qin
        qout[:,1] = -qin[:,1]
        qout[:,2] = -qin[:,2]
        qout[:,3] = -qin[:,3]
        qout[qout == -0.] = 0
        return np.squeeze(qout)
        
    @staticmethod
    def qvqc(qin,v):
        qin = np.matrix(qin)
        v = np.matrix(v)
        
        numq = qin.shape[0]
        numv = v.shape[0]
        
        if (numq != numv):
            if( numq == 1):
                qin = np.tile(qin,(numv,1))
            else:
                v = np.tile(v,(numq,1))
        zero = np.zeros((max(numv,numq),1))
        v = np.column_stack((zero,v))
        
        vout = np.matrix(QuatUtils.qmult(qin,QuatUtils.qmult(v,QuatUtils.qconj(qin))))[:,1:]
        return vout
        
    @staticmethod
    def qcvq(qin,v):
        qin = QuatUtils.qconj(qin)
        vout = QuatUtils.qvqc(qin,v)
        return vout
    
    @staticmethod
    def qnorm(qin):
        qin = np.matrix(qin)
        norm = np.linalg.norm(qin,axis = 1)
        return norm
    
    @staticmethod
    def getQuat(vi,vf):
        #normalize input
        vi = np.matrix(vi)
        vf = np.matrix(vf)
        
        numvi = vi.shape[0]
        numvf = vf.shape[0]
        
        if (numvi != numvf):
            if( numvi == 1):
                vi = np.tile(vi,(numvf,1))
            else:
                vf = np.tile(vf,(numvi,1))        
        viNorms = np.linalg.norm(vi,axis=1)
        vfNorms = np.linalg.norm(vf,axis=1)
        vi = np.divide(vi,np.transpose(np.tile(viNorms,(3,1))))
        vf = np.divide(vf,np.transpose(np.tile(vfNorms,(3,1))))
        
        dotProducts = np.sum(np.multiply(vi,vf),axis = 1)
        q0 = dotProducts+1
        axis = np.cross(vi,vf,axis = 1)
        axisNorms = np.linalg.norm(axis,axis = 1)
        problemAxes = np.where(axisNorms<1.2e-12)
        problemDotProducts = np.where(dotProducts<1.2e-12)
        inds2Fix = np.squeeze(np.where(np.in1d(problemAxes,problemDotProducts)))
        if(np.any(inds2Fix)):
            q0[inds2Fix]=0
            for i in inds2Fix:
                if(vi[i,0]>vi[i,2]):
                    axis[i,:] = [-vi[i,1],vi[i,0],0]
                else:
                    axis[i,:] = [0, -vi[i,2], vi[i,1]]
        axis[axis == -0.] = 0
        
        qout = np.column_stack((q0,axis))
        qoutNorms = np.linalg.norm(qout,axis=1)
        qout =np.divide(qout,np.transpose(np.tile(qoutNorms,(4,1))))
        return qout
        
    @staticmethod
    def correctQuat(inQuat,rotation):
        baseline = np.array([0,0,-1])
        origNormVec = QuatUtils.qvqc(inQuat, baseline)
        oldZ = np.array([0,0,1])
        newZ = QuatUtils.qcvq(rotation,oldZ)
        bpcQuat = QuatUtils.getQuat(newZ,origNormVec)
        return bpcQuat
        
if __name__ == "__main__":
    bpfile =  "05_ENGL_F_biteplate_2.tsv"
    kinfile = "05_ENGL_F_words5.tsv"
    qin = np.array([np.sqrt(2)/2,0,0,np.sqrt(2)/2])
    qout = QuatUtils.qmult(qin,qin)
    output = QuatUtils.qcvq(np.tile(qin,(3,1)),[1,0,0])
    qout = QuatUtils.getQuat(np.tile([0,np.sqrt(2)/2,np.sqrt(2)/2],(2,1)),[0,1,0])
    print qout
    bpcQuat =  QuatUtils.correctQuat(np.tile([0.288723,-0.196910,0.936945,0],(2,1)),np.array([0.9886,-0.0287,-0.0411,0.1423]))
    print bpcQuat
    