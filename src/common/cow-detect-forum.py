#!/usr/bin/env python
#
# heuristic forum detection 
# pass:
# (1) cow.xml file (may be gzipped)
# (2) optionally, an output path 
#     (directories will be created if they
#      do not exist)
# 
# output is gzipped, the output file name
# is determined on the basis of th einout file name
#
#
#
import sys
import re
import gzip
import os


RE_FORUM=r'.*(?:forum|/board/|/threads/|showthread|/archive/(?:index.php/)?t-[0-9]+\.html|viewtopic|ftopic|/\?topic=|(?:/threads/[A-Za-z]+(?:-[A-Za-z]+)+\.[0-9]+/$)|/thread-[0-9]+\.html$|/topic/[0-9]+(?:-[A-Za-z]+)+|/t[0-9]+(?:-[A-Za-z]\+)+\.html)'


def basename(filename):
    return(re.sub('\.xml(?:\.gz)?', '', filename).split("/")[-1])



def main():

    try:
        if sys.argv[1].endswith(".gz"):
            in_h = gzip.open(sys.argv[1], 'rb')
        else:
            in_h = open(sys.argv[1])
    except IOError:
        sys.exit("Cannot open %s\n" %sys.argv[1])

     
    # if an output dir was specified, check if it exists:
    if len(sys.argv) > 2:
        outdir = sys.argv[2].strip().rstrip("/")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
    else:
        outdir = ""

   
    # check if outfile exists:
    outfilename = basename(sys.argv[1]) + ".forum.xml.gz"
    outfullpath = "/".join([i for i in [outdir, outfilename] if len(i) > 0])

    if os.path.exists(outfullpath):
        sys.exit('Outfile %s exists.\n' %outfullpath)
    else:
        out_h = gzip.open(outfullpath, 'wb')
        #out_h = open(outfullpath, 'w')





    for line in in_h:
        line = line.decode('utf8')

        if not line.startswith(u'<doc '):
            out_h.write(line.encode('utf8'))

        else:
            m = re.search(u' url="([^ ]+)"', line)
            if m:
                url = m.group(1)
            else:
                url = ""
            
            if re.match(RE_FORUM, url, re.UNICODE):
                line = re.sub(u'>$', r' forum="1">', line, re.UNICODE)
            else:
                line = re.sub(u'>$', r' forum="0">', line, re.UNICODE)


            out_h.write(line.encode('utf8'))


    in_h.close()
    out_h.close()



if __name__ == "__main__":
    main()
