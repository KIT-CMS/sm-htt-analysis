#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import sys

# Documentation of error codes for covariance matrices
# https://github.com/root-project/root/blob/master/roofit/roofitcore/src/RooFitResult.cxx#L506-L512
"""
case -1 : os << "Unknown, matrix was externally provided" ; break ;
case 0  : os << "Not calculated at all" ; break ;
case 1  : os << "Approximation only, not accurate" ; break ;
case 2  : os << "Full matrix, but forced positive-definite" ; break ;
case 3  : os << "Full, accurate covariance matrix" ; break ;
"""


if __name__ == "__main__":
    filename = sys.argv[1]
    print("[INFO] Check fits from file {}.".format(filename))
    f = ROOT.TFile(filename)

    for name in ["fit_s", "fit_b"]:
        fit = f.Get(name)
        if fit == None:
            raise Exception("[ERROR] {} not found in file {}.".format(name, filename))
        status = fit.status()
        cov_qual = fit.covQual()
        if status == 0 and cov_qual == 3:
            print("[INFO] Fit {} from file {} is ok (status: {}, covQual: {}).".format(name, filename, status, cov_qual))
        else:
            raise Exception("[ERROR] Fit {} from file {} is invalid (status: {}, covQual: {}).".format(name, filename, status, cov_qual))
