"""
   This module contains functions to set up the log-likelihood for the GLM model.      
"""

import numpy as np
from oct2py import octave
from auxiliary_functions import sameconv
from auxiliary_functions import spikeconv
from scipy import linalg


def setupLogL(Stim,tsp,K,H,dt):
    """
    
        Performs preliminary processing of the stimulus and spike trains,
        and returns the negative log-likelihood function and its gradient
        (as functions of the filter coefficients). 
        
        Parameters
        ----------
        Stim : array_like
            Stimulus.
        tsp : array_like 
            Spike times.
        K : array_like
            Stimulus basis.
        H : array_like
            Post-spike basis.
        dt : float
            Discretization step for the likelihood.
            
        Returns
        -------
        fun : function
            Evaluates the negative log-likelihood.
        fun_grad : function
            Evaluates the gradient of the negative log-likelihood.
            
        

        Notes
        -----
        Using one neuron
        
        It requires the global variable path_to_spikeconv_mex.
        It requires octave installation and addition of the octave path.


               
    """
    
    # add the path to the external octave function
    global path_to_spikeconv_mex
    #path_to_spikeconv_mex = os.getcwd()+'/external'
    #path_to_spikeconv_mex = '/Users/val/Desktop/code_GLM_v1_Feb2010/mex_tools'
    #octave.addpath(path_to_spikeconv_mex)    
    
    
    RefreshRate = 100
    nofBins = int(1/dt)
    
    dim_k = K.shape[1]
    
    # convert the spiking times to the new sampling lattice (to integers)
    tsp_int = np.ceil((tsp - dt*0.001)/dt)
    tsp_int = np.reshape(tsp_int,(tsp_int.shape[0],1))
    tsp_int = tsp_int.astype(int)

    # run spikeconv_mex from octave path 
    # M_h = octave.spikeconv_mex(tsp_int,H,np.array([1,Stim.shape[0]/dt]))
    M_h = spikeconv(tsp_int,H,np.array([1,Stim.shape[0]/dt]))

    # convolving the stimulus with each basis function
    Stim_convolved = sameconv(Stim,K)

    # interpolating at the locations determined by nofBins
    m = Stim_convolved.shape[0]
    M_k = np.zeros((nofBins*m,dim_k)) # this will fail for one dimensional K
    for i in np.arange(dim_k):
        M_k[:,i] = np.interp(np.linspace(0,m,nofBins*m),np.arange(m),Stim_convolved[:,i])

    # create a function evaluating the likelihood
    def fun(pars):
        
        coeff_k = pars[:M_k.shape[1]]
        coeff_h = pars[M_k.shape[1]:]
        
        # calculate the conditional intensity
        cond_intensity = np.exp(np.dot(M_k,coeff_k)+np.dot(M_h,coeff_h))
    
        # fix the starting points  
        tspi = 1
        start_idx = 1

        trm1 = -sum(np.log(cond_intensity[tsp_int[tspi:]]))[0]  # Spiking term
        trm2 = sum(cond_intensity[start_idx:])*dt/RefreshRate # Non-Spiking term

        return(trm1 + trm2)
        
    def fun_grad(pars):
        
        # extracting the coefficients
        coeff_k = pars[:M_k.shape[1]]
        coeff_h = pars[M_k.shape[1]:]

        # non-spiking terms
        dLdk = (np.dot(np.exp(np.dot(M_k,coeff_k) + np.dot(M_h,coeff_h)),M_k))*dt/RefreshRate
        dLdh = (np.dot(np.exp(np.dot(M_k,coeff_k) + np.dot(M_h,coeff_h)),M_h))*dt/RefreshRate
        
        # spiking terms
        dLdk = dLdk - sum(M_k[np.hstack(tsp_int),:])
        dLdh = dLdh - sum(M_h[np.hstack(tsp_int),:])
        
        return(np.hstack((dLdk,dLdh)))
        
    return(fun,fun_grad)
    
def construct_covariates(Stim,tsp,K,H,dt):
    """
    
        Performs preliminary processing of the stimulus and spike trains,
        and returns the negative log-likelihood function and its gradient
        (as functions of the filter coefficients). 
        
        Parameters
        ----------
        Stim : array_like
            Stimulus.
        tsp : array_like 
            Spike times.
        K : array_like
            Stimulus basis.
        H : array_like
            Post-spike basis.
        dt : float
            Discretization step for the likelihood.
            
        Returns
        -------
        fun : function
            Evaluates the negative log-likelihood.
        fun_grad : function
            Evaluates the gradient of the negative log-likelihood.
            
        

        Notes
        -----
        Using one neuron
        
        It requires the global variable path_to_spikeconv_mex.
        It requires octave installation and addition of the octave path.


               
    """
    
    
    
    RefreshRate = 100
    nofBins = int(1/dt)
    
    dim_k = K.shape[1]
    
    # convert the spiking times to the new sampling lattice (to integers)
    tsp_int = np.ceil((tsp - dt*0.001)/dt)
    tsp_int = np.reshape(tsp_int,(tsp_int.shape[0],1))
    tsp_int = tsp_int.astype(int)

    # run spikeconv_mex from octave path 
    # M_h = octave.spikeconv_mex(tsp_int,H,np.array([1,Stim.shape[0]/dt]))
    M_h = spikeconv(tsp_int,H,np.array([1,Stim.shape[0]/dt]))

    # convolving the stimulus with each basis function
    Stim_convolved = sameconv(Stim,K)

    # interpolating at the locations determined by nofBins
    m = Stim_convolved.shape[0]
    M_k = np.zeros((nofBins*m,dim_k)) # this will fail for one dimensional K
    for i in np.arange(dim_k):
        M_k[:,i] = np.interp(np.linspace(0,m,nofBins*m),np.arange(m),Stim_convolved[:,i])
        
    M = np.hstack((M_k,M_h))
    return(M)