# -*- coding: utf-8 -*-

# Write values of 'crx'-attributes to csv file.

import os.path
import sys
import glob
import re
from lxml import etree as ET
import operator


NOTNORMALIZED = ['crx_alltokc', 'crx_sentc', 'crx_tokc', 'crx_ttrat', 'crx_vflen', 'crx_wlen', 'crx_slen', 'crx_indefraw', 'crx_clitindefraw']

#NOTOUTPUT = ['crx_alltokc', 'crx_sentc', 'crx_tokc']

def get_corex_attrs(dom):
    # get all attributes and values of doc:
    attrvaldict = dom.attrib
    # get rid of all non-corex attributes:
    for attr in attrvaldict:
        if not attr.startswith('crx_'):
            del attrvaldict[attr]
    return(attrvaldict)


def prop2count(attrvaldict):
    newdict = dict()
    for attr in NOTNORMALIZED:
        if attr in ['crx_ttrat', 'crx_vflen', 'crx_wlen', 'crx_slen']:
            newdict[attr] = float(attrvaldict[attr])
        else:
            newdict[attr] = int(attrvaldict[attr])

    # convert these back to raw counts first, as they are used to normalize
    # other counts:
    tokc = float(attrvaldict['crx_tokc'])
    sentc = float(attrvaldict['crx_sentc'])

    for attr in ['crx_simpx', 'crx_psimpx', 'crx_rsimpx']:
        newdict[attr] = int(round(float(attrvaldict[attr])*sentc))


    for attr in ['crx_v2', 'crx_vlast']:
        newdict[attr] = int(round(float(attrvaldict['crx_vv'])* (tokc/1000), 0))


    newdict['crx_vv'] = int(round(float(attrvaldict['crx_vv'])* (tokc/1000), 0))
    newdict['crx_cn'] = int(round(float(attrvaldict['crx_cn'])* (tokc/1000), 0))




    # convert all other values back to raw counts:

    # skip attributes that were already converted:
    for attr in attrvaldict:
        if attr in NOTNORMALIZED + ['crx_simpx', 'crx_psimpx', 'crx_rsimpx', 'crx_v2', 'crx_vlast', 'c_vf', 'crx_cn', 'crx_vv']:
            continue

        if attr in ['crx_pass', 'crx_perf', 'crx_plu']:
            n = int(newdict['crx_simpx']) + int(newdict['crx_psimpx']) + int(newdict['crx_rsimpx'])

        elif attr in ['crx_esvf', 'crx_clausevf']:
            n = int(newdict['crx_v2'])

        elif attr in ['crx_vvieren', 'crx_cogverb', 'crx_dicverb', 'crx_reprverb', 'crx_dirverb', 'crx_commissverb', 'crx_exprverb', 'crx_declverb']:
            n = int(newdict['crx_vv'])

        elif attr in ['crx_cmpnd', 'crx_loan']:
            n = int(newdict['crx_cn'])

        else:
            n = tokc

        newdict[attr] = int(round(float(attrvaldict[attr])* (n/1000), 0))
    return(newdict)



def write_line(csv_h, docid, docattrvaldict):
    reforder = ['crx_ttrat',
            'crx_wlen',
            'crx_slen',
            'crx_mod',
            'crx_vv',
            'crx_vaux',
            'crx_vfin',
            'crx_cn',
            'crx_prep',
            'crx_inf',
            'crx_imp',
            'crx_adv',
            'crx_adj',
            'crx_subjs',
            'crx_subji',
            'crx_conj',
            'crx_wh',
            'crx_dem',
            'crx_poss',
            'crx_neg',
            'crx_answ',
            'crx_zuinf',
            'crx_parta',
            'crx_card',
            'crx_itj',
            'crx_nonwrd',
            'crx_def',
            'crx_indef',
            'crx_neper',
            'crx_neloc',
            'crx_neorg',
            'crx_emo',
            'crx_dq',
            'crx_clitindef',
            'crx_vpast',
            'crx_vpres',
            'crx_vpressubj',
            'crx_wpastsubj',
            'crx_vvpastsubj',
            'crx_pper_1st',
            'crx_pper_2nd',
            'crx_pper_3rd',
            'crx_gen',
            'crx_simpx',
            'crx_psimpx',
            'crx_rsimpx',
            'crx_v2',
            'crx_vlast',
            'crx_vflen',
            'crx_esvf',
            'crx_clausevf',
            'crx_cmpnd',
            'crx_unkn',
            'crx_short',
            'crx_qsvoc',
            'crx_cnloan',
            'crx_vvieren',
            'crx_sapos',
            'crx_pass',
            'crx_perf',
            'crx_plu',
            'crx_indefraw',
            'crx_clitindefraw',
            'crx_excl',
            'crx_ques',
            'crx_exclques',
            'crx_cogverb',
            'crx_dicverb',
            'crx_reprverb',
            'crx_dirverb',
            'crx_commissverb',
            'crx_exprverb',
            'crx_declverb'
           ]

    outlist = [docid]
    for attr in reforder:
        try:
            outlist.append(str(docattrvaldict[attr]))
        except KeyError:
            msg = "Doc %s: no attribute %s (set to 0)\n" %(docid, attr)
            sys.stderr.write(msg.encode('utf8'))
            outlist.append("0")
    line = "\t".join(outlist) + "\n"
    csv_h.write(line.encode('utf8'))




def write_csv(dom, csv_h):
    docid = dom.get('id')
    attrvaldict = get_corex_attrs(dom)
    attrvaldict = prop2count(attrvaldict)
    write_line(csv_h, docid, attrvaldict)








