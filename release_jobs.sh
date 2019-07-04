#!/bin/bash

condor_qedit -constraint 'JobStatus=?=5' -owner ${1} JobRunCount 1
condor_qedit -constraint 'JobStatus=?=5' -owner ${1} NumJobMatches 1
condor_qedit -constraint 'JobStatus=?=5' -owner ${1} NumJobStarts 1
condor_qedit -constraint 'JobStatus=?=5' -owner ${1} NumShadowStarts 1
condor_qedit -constraint 'JobStatus=?=5' -owner ${1} NumShadowExceptions 1
condor_release ${1}
