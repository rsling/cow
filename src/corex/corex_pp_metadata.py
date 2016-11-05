#!/usr/bin/python
# -*- coding: utf-8 -*- 

# This reads a file of doc elements (gzipped), one per line,
# and pretty-prints the values of attributes (alphabetically)
# to outfile (.gz). Output format is tab separated values.
# 
# pass: <infile> <outfile>

import sys
import re
import gzip


def split_germanet(attrval_tuples):
    germanet = [(attr, val) for (attr, val) in attrval_tuples if attr == 'crx_sem']
    rest = [(attr, val) for (attr, val) in attrval_tuples if attr != 'crx_sem']
    if len(germanet) > 0:
        valstring = germanet[0][1]
        sattrval_strings = valstring.split(',')
        sattrvals_strings = [string for string in sattrval_strings if len(string) > 0]
        sattrval_tuples = [("crx_sem_" + s.split(':')[0].strip(), (s.split(':')[1].strip())) for s in sattrval_strings]
        germanet = sorted(sattrval_tuples) 
    attrval_tuples = rest + germanet
    return(attrval_tuples)
        

def filter_attrs(attrval_tuples):
    corex = [(attr, val) for (attr, val) in attrval_tuples if attr.startswith('crx_')]
    other = sorted([(attr, val) for (attr, val) in attrval_tuples if attr in ['id', 'url']])
    attrval_tuples = other + corex 
    return(attrval_tuples)


def get_attrvals(line):
    attrdict = dict()
    line = line.strip().replace('<doc', '').replace('>', '')#.replace('"', '')
    # fill 'empty' values with dummy '_':
    line = re.sub(u'=" *"' , u'="_"', line) 
    # split after attr/val pairs:
    attrval_strings = line.split('" ')
    # filter out potentially empty strings as list elements:
    attrval_strings = [string for string in attrval_strings if len(string) > 0]
    # make list of (attr, val) tuples:
    try:
        attrval_tuples = [(s.split('="')[0].strip(), (s.split('="')[1].strip())) for s in attrval_strings]
    except IndexError:
        print("\nIndex error in this line: ")
        print(line)
        print("\nattrval_strings:")
        print(attrval_strings) 
        print("\nattrval_tuples:")
        print(attrval_tuples)
        raise
    
    attrval_tuples = filter_attrs(attrval_tuples)
    attrval_tuples = split_germanet(attrval_tuples)

    attrsline = "\t".join([attr for (attr, val) in attrval_tuples])
    valsline = "\t".join([val for (attr, val) in attrval_tuples])
    return(attrsline, valsline)
    

def check_attr_order(attrsline, reference_attrsline):
    if len(reference_attrsline) > 0:
        if attrsline != reference_attrsline:
            return(False)
        else:
            return(True)
    else:
        return(True)
        

def prettyprint_docattributes(line, metadatafile, reference_attrsline, doccounter):
    if not line.startswith('<doc'):
            sys.stderr.write("\nLine " + str(doccounter) + ": not a doc element.\n" + str(line.encode('utf8')) + "\n")
            sys.exit(1)
    (attrsline, valsline) = get_attrvals(line)
    if doccounter == 1:
        reference_attrsline = attrsline
        metadatafile.write(reference_attrsline.encode('utf8') + "\n")
    if check_attr_order(attrsline, reference_attrsline) == True:
        metadatafile.write(valsline.encode('utf8') + "\n")
    else:
        sys.stderr.write("\nLine " + str(doccounter) + ": attributes not in same order as reference.\n" + attrsline.encode('utf8') + "\n" + reference_attrsline)
    return(reference_attrsline )



def main():
    
    if not len(sys.argv) == 3:
        sys.stderr.write("\nArguments must be <infile> <outfile>\n\n")
        sys.exit(1)

#    infile = gzip.open(sys.argv[1], "r")
#    outfile = gzip.open(sys.argv[2], "w")

    infile = open(sys.argv[1], "r")
    outfile = open(sys.argv[2], "w")


    doccounter = 0
    reference_attrsline = "" 

    for line in infile:
        line = line.decode('utf8')
        doccounter += 1
        prettyprint_docattributes(line, outfile, reference_attrsline, doccounter)
    
          
    sys.stderr.write("\nTotal documents: " + str(doccounter) + "\n")
    infile.close()
    outfile.close()

if __name__ == "__main__":
    main()


