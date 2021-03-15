import os
import sys
import argparse
from nsdcode.nsd_mapdata import NSDmapdata
from nsdcode.nsd_datalocation import nsd_datalocation

def argument_parse():
    parser=argparse.ArgumentParser(description='Transform NSD data from the command line')
    
    parser.add_argument('--nsdlocation',action='store',dest='basedir',default=None)
    parser.add_argument('--subjix',action='store',dest='subjix',type=int)
    parser.add_argument('--sourcespace',action='store',dest='sourcespace')
    parser.add_argument('--targetspace',action='store',dest='targetspace')
    parser.add_argument('--sourcedata',action='store',dest='sourcedata')
    parser.add_argument('--interptype',action='store',dest='interptype',default=None)
    parser.add_argument('--badval',action='store',dest='badval',default=None)
    parser.add_argument('--outputfile',action='store',dest='outputfile')
    parser.add_argument('--outputclass',action='store',dest='outputclass',default=None)
    parser.add_argument('--fsdir',action='store',dest='fsdir',default=None)
    parser.add_argument('--transformfile',action='store',dest='transformfile',default=None)
    
    return parser.parse_args()
    
if __name__ == "__main__":
    args=argument_parse()
    #if transform file was provided, we can ignore the basedir and subjix and just set defaults
    if args.transformfile is not None:
        if args.basedir is None:
            args.basedir=nsd_datalocation(".")
        if args.subjix is None:
            args.subjix=1
    NSD=NSDmapdata(args.basedir)
    NSD.fit(args.subjix,
            args.sourcespace,
            args.targetspace,
            args.sourcedata,
            args.interptype,
            args.badval,
            args.outputfile,
            args.outputclass,
            args.fsdir,
            args.transformfile,
            )