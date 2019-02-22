#!/usr/bin/python
#-*-coding: utf-8 -*-

import re
import sys
import gzip 
import time
from argparse import ArgumentParser
import logging


def arguments():
    parser = ArgumentParser(description="Extracts all meta data from COW-XML doc headers. Performs a check on the (intended) data type. Values will appear in the output csv file in the exact same order as listed in the 'attributes' file, irrespective of their order in the document headers. Attributes missing from individual document headers will be inserted with value 'unknown'.")
    parser.add_argument('attributes', help="A file describing expected attributes and data type of values: one attr-type pair per line, attr and type separated by TAB. Valid types are: 'char', 'int', 'float'.")
    parser.add_argument('infile', help='COW-XML infile: utf-8 encoded, may be gzipped')
    parser.add_argument('-d', '--debug', action="store_true", default=False, help='print debug messages')
    parser.add_argument('-v', '--verbose', action="store_true", default=False, help='print warning messages')
#    parser.add_argument('--extension', help='the file name extension of input files; with this option, both output and log info will be written to appropriately named files rather than to stdout/stderr')


    args = parser.parse_args()
    return(args)



def basename(orginal, suffix):
    return(re.sub(suffix, '', orig))



def mk_attrval_dict(attrval_fh):
    """Read a tab-separated attributes file,
    return a dictionary containing valid attribute names
    and expected data types; also return a list of attribute names
    in the same order as specified in attributes file"""
    attrval_dict = dict()
    attr_sequence = list()
    lc = 0
    for line in attrval_fh:
        lc += 1
        line = line.decode('utf-8').strip()
        if line:
            if not line.startswith('#'):
                attrval = line.split("\t")
                if not len(attrval) == 2:
                    msg = "Syntax error in attributes file, line %d: %s\n" %(lc, line)
                    sys.exit(msg.encode('utf-8'))
                if attrval[0] in attrval_dict:
                    logging.critical("Attribute '%s' specified multiple times." %attrval[0])
                    sys.exit(1)
                # record sequence of attributes in attributes file:
                attr_sequence.append(attrval[0])
                if attrval[1] in ['int', 'char']:
                    attrval_dict[attrval[0]] = [attrval[1], [0], [""]]
                elif attrval[1] == 'float':
                    attrval_dict[attrval[0]] = [attrval[1], [0,0], ["",""]]
                else:
                    logging.critical("Value type '%s' undefined, line %d; must be one of 'int', 'float', 'char'" %(attrval[1], lc))
                    sys.exit(1)
 
    return(attrval_dict, attr_sequence)


def init_dict(reference_dict):
    newdict = dict()
    for attr in reference_dict:
        newdict[attr] = "unknown"
    return(newdict)


def data_type(val):
    """Examines a string, determines 'intended' data type and length"""
    # default type is char:
    dtype = (u'char', len(val))
    logging.debug("Trying data type 'float'...")
    # type is float if string can be converted without errors:
    if re.match('^-?(?:[0-9]+\.?[0-9]*|[1-9]\.[0-9]+[eE]-?[0-9]*)$', val):
        try:
            newval = '{:.5f}'.format(float(val)) # this is for scientific notation in attributes from texrex
            parts = newval.split(".")
            seq1 = len(parts[0].lstrip('-'))
            try:
                seq2 = len(parts[1])
            except IndexError:
                seq2 = 0
            dtype = (u'float', (seq1 + seq2, seq2))
            logging.debug("... is a float.")
        except ValueError:
            pass
    # type is int if string can be converted without errors:
    logging.debug("Tryng data type 'int'...")
    try:
        int(val)
        dtype = (u'int', len(val.lstrip('-')))
        logging.debug("... is an int.")
    except ValueError:
        pass        
    return(dtype)


def basename(origname):
    return(re.sub("\.xml(\.gz)?$", "", origname))




def main():
    args = arguments()

    if args.debug:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    if args.verbose:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARNING)
    else:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

    
    try:
        attr_h = open(args.attributes)
        attrval_dict, attr_sequence =  mk_attrval_dict(attr_h)
        if args.debug:
            for i in attrval_dict:
                logging.debug(i),
                logging.debug(attrval_dict[i])
    except IOError:
        sys.exit("Cannot open attributes file.")



    try:
        if args.infile.endswith(".gz"):
            in_h = gzip.open(args.infile)
        else:
            in_h = open(args.infile)
    except IOError:
        sys.exit("Cannot open infile.")
   

 #   if args.extension:
 #       basen = basename(args.infile, args.extension)
#
        outfile = basen + ".meta.csv.gz"
#        if os.path.exists(outfile):
#            exit("Outfile %s exists." %outfile)
#        else:
#            out_h =  gzip.open(outfile, 'wb')





    doccount = 0
    linecount = 0

    for line in in_h:
        linecount += 1
        line = line.decode('utf-8').strip()
        if line.startswith(u'<doc '):
            doccount += 1
            this_doc_dict = init_dict(attrval_dict)

            # remove beginning and end of line:
            line = re.sub('^<doc +', '', line)
            line = line.rstrip('">')
            # remove whitespace in instances such as: date=" 1.1.1997"
            line = re.sub('=" +(?![a-z_]+=")', '="' ,line)
            avpairs = re.split(u'"[ >]+', line)
            logging.debug(avpairs)
            attrs = [av.split("=")[0] for av in avpairs]
            logging.debug("Doc %d (line %d): %d attributes" %(doccount, linecount, len(attrs)))
           
            # check if doc head has all attributes specified in attribute file
            if not attrs == attr_sequence:
                missing_attrs = [attr for attr in attr_sequence if not attr in attrs]
                if len(missing_attrs) > 0:
                    logging.warning("Missing attributes in doc %d (line %d): %s ==> inserting 'unknown'" %(doccount, linecount, ", ".join(missing_attrs)))

            # check data type of every value:
            for pair in avpairs:
                logging.debug(pair)
                attr = pair.split("=")[0].strip('"')
                val = pair.split("=")[1].strip('"')
                dtype = data_type(val)
                if not dtype[0] == attrval_dict[attr][0]:
                        # in case of mismatch, be allow for some flexibility:
                        #
                        # sometimes, a char value can be interpreted as an integer (e.g., forum="1"): 
                        if attrval_dict[attr][0] == 'char':
                            logging.info("Doc %d (line %d): Value '%s' of attribute '%s' is %s, but only 'char' required."  %(doccount, linecount, val, attr, dtype[0]))
                        # sometimes, a float can be interpreted as an integer (e.g., nbcprop="1")
                        elif attrval_dict[attr][0] == 'float' and dtype[0] == 'int':
                            logging.info("Doc %d (line %d): Value '%s' of attribute '%s' is 'int', but 'float' required."  %(doccount, linecount, val, attr))
                        # all other mismatches are treated as critical:
                        else:
                            logging.critical("Doc %d (input line %d): Value '%s' of attribute '%s' is of type '%s', but %s required." %(doccount, linecount, val, attr, dtype[0], attrval_dict[attr][0]))
                            sys.exit(1)
                
                # when there is no critical type mismatch,
                # check length of value and record it
                # in case it is the longest val so far: 
                if dtype[0] in ['int','char']:
                    if dtype[1] >  attrval_dict[attr][1][0]:
                        attrval_dict[attr][1][0] = dtype[1]
                        attrval_dict[attr][2][0] = val
                elif dtype[0] == 'float':
                    if dtype[1][0] > attrval_dict[attr][1][0]:
                         attrval_dict[attr][1][0] = dtype[1][0]
                         attrval_dict[attr][2][0] = val
                    if dtype[1][1] > attrval_dict[attr][1][1]:
                         attrval_dict[attr][1][1] = dtype[1][1]
                         attrval_dict[attr][2][1] = val

                else:
                    logging.error("Unkown data type: %s\n" %dtype[0])
                    sys.exit(1)

                # if attribute was specified in attribute file,
                # record val fpr this document; if not, fail.
                if attr in this_doc_dict:
                    this_doc_dict[attr] = val
                else:
                    logging.error("Do %d (input line %d): attribute '%s' not declared in attributes file.\n" %(doccount, linecount, attr))
                    sys.exit(1)

            # format output for this document and print
            b = list()
            for attr in attr_sequence:
                b.append(this_doc_dict[attr])
            print("\t".join(b).encode('utf-8'))


    # print summary statistics:
    sys.stderr.write("\n---------- Summary ----------\n")
    sys.stderr.write(("Attribute names:\t" + "\t".join(attr_sequence) + "\n").encode('utf-8'))
    sys.stderr.write(("Total number of attributes:\t" + str(len(attr_sequence))+ "\n").encode('utf-8'))
    sys.stderr.write("\nMaximal length of values:\n\n".encode('utf-8'))
    for attr in attrval_dict:
        attrval_dict[attr][1] =  [str(i) for i in attrval_dict[attr][1]]
    for attr in attr_sequence:
        output = [attr, attrval_dict[attr][0], ",".join(attrval_dict[attr][1]), ", ".join(attrval_dict[attr][2])]
        sys.stderr.write(("\t".join(output) + "\n").encode("utf-8"))



if __name__ == "__main__":
    main()





