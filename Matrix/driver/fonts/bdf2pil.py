
import os
import argparse
from PIL import BdfFontFile
from PIL import PcfFontFile


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
   
    parser.add_argument("-b", "--bdf", help="source bdf file")
    
    args = parser.parse_args()
    
    source = args.bdf
    dest = source.replace(".bdf", ".pil")

    with open(source,'rb') as fp:
        p = BdfFontFile.BdfFontFile(fp) #PcfFontFile if you're reading PCF files
        p.save(dest)
   