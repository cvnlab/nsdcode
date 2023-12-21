import os
import sys
import argparse
import textwrap
from nsdcode.nsd_mapdata import NSDmapdata
from nsdcode.nsd_datalocation import nsd_datalocation

def argument_parse():
    parser=argparse.ArgumentParser(description='Transform NSD data from the command line',
        epilog=textwrap.dedent('''\
        --sourcespace and --targetspace options include: 
            anat0pt5, anat0pt8, anat1pt0, func1pt0, func1pt8, MNI,
            [lh,rh].white, [lh,rh].pial, [lh,rh].layerB1, [lh,rh].layerB2, [lh,rh].layerB3, fsaverage'''))
    
    parser.add_argument('--sourcespace',action='store',dest='sourcespace',help="One of the volume/surface space options below",required=True)
    parser.add_argument('--targetspace',action='store',dest='targetspace',help="One of the volume/surface space options below",required=True)
    parser.add_argument('--inputfile',action='store',dest='inputfile',help="Input file in <sourcespace>",required=True)
    parser.add_argument('--outputfile',action='store',dest='outputfile',help="Output file in <targetspace>",required=True)
    parser.add_argument('--nsdlocation',action='store',dest='basedir',default=None,help='Directory containing ppdata/, etc')
    parser.add_argument('--subjix',action='store',dest='subjix',type=int,help="NSD subject index 1-8")
    parser.add_argument('--interptype',action='store',dest='interptype',default='cubic',
        choices=['nearest','linear','cubic','wta','surfacewta'],
        help="default: 'cubic'. See nsd_mapdata.py for wta details")
    parser.add_argument('--badval',action='store',dest='badval',default=None)
    parser.add_argument('--outputclass',action='store',dest='outputclass',default=None)
    parser.add_argument('--fsdir',action='store',dest='fsdir',default=None)
    parser.add_argument('--transformfile',action='store',dest='transformfile',default=None,
        help="Manually-specified transformation file (ignores --nsdlocation and --subjix)")
    
    return parser.parse_args()

def main():
    args=argument_parse()
    #if transform file was provided, we can ignore the basedir and subjix and just set defaults
    if args.transformfile is not None:
        if args.basedir is None:
            args.basedir=nsd_datalocation(".")
        if args.subjix is None:
            args.subjix=1
    NSD=NSDmapdata(args.basedir)
    NSD.fit(subjix=args.subjix,
            sourcespace=args.sourcespace,
            targetspace=args.targetspace,
            sourcedata=args.inputfile,
            interptype=args.interptype,
            badval=args.badval,
            outputfile=args.outputfile,
            outputclass=args.outputclass,
            fsdir=args.fsdir,
            transformfile=args.transformfile,
            )
        
    
if __name__ == "__main__":
    main()