#!/usr/bin/python
# -*- coding: utf-8 -*- 

# This script removes all xml-Elements outside of s-Elements, except for doc.
# Useful for removing topo-parse annotations outside of <s ...> ... </s> regions.
#
# pass: infile outfile (both gzipped)

import sys
import gzip


def main():

    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], "w")


    within_s = False

    for line in infile:
        line = line.decode('utf8')
#        print("1"),
#        print(within_s)
#        print(line.encode('utf8'))
        # enter a sentence region:
        if line.startswith('<s>') or line.startswith('<s '):
            within_s = True
#            print('2 Sstart')
#            print(within_s)
        
        if within_s == True:
            outfile.write(line.encode('utf8'))
#            print('3 Keep this line')
       
        if line.startswith('</s>'):
            within_s = False
#            print('4 Send')
 #           print(within_s)
        
        if within_s == False:
            if not line.startswith('<') or line.startswith('<doc ') or line.startswith('</doc>'):
#                print('5 Keep this line, is token or <doc> </doc>') 
                outfile.write(line.encode('utf8'))
                                  
#            else:
                #print(line.encode('utf8'))
#                print('6 Dump this line')
                
              

if __name__=="__main__":
    main()


