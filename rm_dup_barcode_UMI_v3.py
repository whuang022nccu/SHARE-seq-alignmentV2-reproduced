
'''
This script accept a input sorted sam file, a output sam file, and a mismatch rate, then it will remove
duplicates based on the barcode + UMI (edit distance <= 1), and chromatin and start site, at the same
time, it will output the duplication number for each read, and generate the histogram plot for the read
per duplication number
'''
import os
import re
import sys
from Levenshtein import distance
import sys
import matplotlib as mpl
import numpy as np
mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from optparse import OptionParser
import time
import io

# sys.setrecursionlimit(1000000)
      

if __name__ == "__main__":
    start = time.process_time()
    opts = OptionParser()
    usage = "usage: %prog [options] [inputs] This will remove UMI duplicates"
    opts = OptionParser(usage=usage)
    opts.add_option("-i", help="<input> bam file")
    opts.add_option("-o", help="<output> tsv file")
    opts.add_option("--m", help="<mismatch> number of mismatch", default="1")
    options, arguments = opts.parse_args()
    
    # return usage information if no argvs given
    if len(sys.argv)==1:
        os.system(sys.argv[0]+" --help")
        sys.exit()
    file_in = options.i
    file_out = options.o
    mismatch = options.m
 
    filein = io.BufferedReader(open(file_in, 'rb'))
    fileout = io.BufferedWriter(open(file_out, 'wb'))

    pre_chrom = 0
    pre_site = 0
    pre_gene=0
#    pre_barcode=0

    mismatch=int(mismatch)
    count = 0
    dups = 0
    umiset = dict()
    countset = dict()

    print("Allow " + str(mismatch) + " mismatch for UMIs")
    newposition = False
    while 1:
        line = filein.readline().strip().decode()
        if len(line) == 0:
            break
        count = count + 1
        
        read = line.split('\t')
        chrom_num = read[0]
        start_site = read[1]
        barcode = read[2]
        umi = read[3]
        gene = read[4]
        
#        print(line)
        ## same starting pos and barcode
        if umi != "GGGGGGGGGG":
            if ((start_site == pre_site) and (chrom_num == pre_chrom)):
                newposition = False
#                print("old position")
                if barcode in umiset.keys():
                    value = umiset[barcode]
                    eachumi = value[0]
                    num = value[1]
                    if distance(umi, eachumi) <= mismatch:
                        # print("found umi")
                        num += 1
                        umiset[barcode] = [umi, num]
                        dups += 1
                    else:
                        # print("new UMI")
                        umiset[barcode] = [umi, 1]      
                else:
                    umiset[barcode] = [umi, 1]
                    # print("new bc")
            else:
                newposition = True
                for key, value in umiset.items():
                    newline = key + '\t' + pre_gene + '\t' + str(value[1]) + '\t' + value[0] + '\n'
#                    print(newline)
                    fileout.write(str.encode(newline))

                umiset = dict()
                umiset[barcode] = [umi, 1]
                pre_site = start_site
                pre_chrom = chrom_num
                pre_gene = gene
                
    # after looping print last line
    if (newposition == True):
        newline = barcode + '\t' + gene + '\t' + str(1) + '\t' + umi + '\n'
        #   print(newline)
        fileout.write(str.encode(newline))
    else:
        for key, value in umiset.items():
            newline = key + '\t' + pre_gene + '\t' + str(value[1]) + '\t' + value[0] + '\n'
            #                    print(newline)
            fileout.write(str.encode(newline))

    print("total reads: " + str(count))
    print("total dup reads: " + str(dups))
    filein.close()
    fileout.close()
    time = (time.process_time() - start)/60
    print("%.2g" % time + " min consumed")
    sys.exit()
