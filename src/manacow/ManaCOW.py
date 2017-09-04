#!/usr/bin/python

import manatee
import os
import itertools
import random
import time
import sys
import re
from time import gmtime, strftime

def isplit(iterable, splitters):
  return [list(g) for k,g in itertools.groupby(iterable, lambda x: x in splitters)]

flatten = lambda l: [item for sublist in l for item in sublist]

os.environ['MANATEE_REGISTRY'] = '/var/lib/manatee/registry'


DEFAULT_CORPUS     = 'decow16a-nano'
DEFAULT_ATTRS      = ['word', 'tag', 'lemma', 'depind', 'dephd', 'deprel']
DEFAULT_STRUCTURES = ['s', 'nx']
DEFAULT_REFS       = ['doc.corex_clitindef', 'doc.corex_short', 'doc.corex_emo', 'doc.corex_gen',
  'doc.corex_slen', 'doc.corex_wlen', 'doc.corex_pper_2nd', 'doc.corex_ttrat', 'doc.country', 'doc.url',
  'doc.bdc', 'doc.tld', 'doc.id', 'doc.urldomain', 'doc.forum', 'div.bpc', 's.idx', 's.type']


# Make a query and return a raw conordance dictionary.
def cow_query(query, corpus = DEFAULT_CORPUS,
  container = 's', max_hits = -1, random_subset = -1, deduping = False,
  context_left = 0, context_right = 0,
  attributes = DEFAULT_ATTRS, structures = DEFAULT_STRUCTURES,
  references = DEFAULT_REFS):

  result = list()

  # Set up and run query.
  h_corpus  = manatee.Corpus(corpus)
  h_region  = manatee.CorpRegion(h_corpus, ','.join(attributes), ','.join(structures))
  h_cont    = h_corpus.get_struct(container)
  h_refs    = [h_corpus.get_attr(r) for r in references]
  start_time = time.time()
  results   = h_corpus.eval_query(query)

  # Process results.
  counter  = 0
  dup_no   = 0
  if deduping: dups = dict()
  while not results.end() and (max_hits < 0 or counter < max_hits):

    # Skip randomly if random subset desired.
    if random_subset > 0 and random.random() > random_subset:
      results.next()
      continue

    kwic_beg = results.peek_beg()                             # Match begin.
    kwic_end = results.peek_end()                             # Match end.
    cont_beg_num = h_cont.num_at_pos(kwic_beg)-context_left   # Container at match begin.
    cont_end_num = h_cont.num_at_pos(kwic_beg)+context_right  # Container at match end.

    # If hit not in desired region, drop.
    if cont_beg_num < 0 or cont_end_num < 0:
      results.next()
      continue

    cont_beg_pos = h_cont.beg(cont_beg_num)                   # Pos at container begin.
    cont_end_pos = h_cont.end(cont_end_num)                   # Pos at container end.
    
    # TODO RS Memory and time (likely malloc, CPU load actually *lower*) lost in next 2 lines!
    refs = [h_refs[i].pos2str(kwic_beg) for i in range(0, len(h_refs))]
    region = h_region.region(cont_beg_pos, cont_end_pos, '\t', '\t')
    
    # Deduping.
    if deduping:
      dd_region = ''.join([region[i].strip().lower() for i in range(0, len(region), 1+len(attributes))])
      if dd_region in dups:
        dup_no += 1
        results.next()
        continue
      else:
        dups.update({dd_region : 0})

    result.append({'match_offset' : kwic_beg - cont_beg_pos, 'match_length' : kwic_end - kwic_beg, 'meta' : refs, 'region' : region })

    # Advance stream/loop.
    results.next()
    counter += 1

  end_time = time.time()
  result = { 'query' : query.encode('utf-8'), 'corpus' : corpus, 'container' : '<'+container+'/>', 'hits' : counter, 'max_hits' : max_hits, \
    'random_subset' : random_subset, 'context_left' : context_left, 'context_right' : context_right, 'attributes' : attributes, \
    'structures' : structures, 'references' : references, 'datetime' : strftime("%Y-%m-%d %H:%M:%S", gmtime()), \
    'elapsed' : end_time-start_time, 'deduping' : str(deduping), 'duplicates' : dup_no, 'concordance' : result }

  return result


# Format a Manatee region as raw concordance line.
def cow_region_to_conc(region, attrs = True):
  if not attrs:
    conc = filter(lambda x: x not in ['strc', 'attr', '{}'], region)
    conc = [[words] for segments in conc for words in segments.split()]
  else:
    conc = isplit(region, ['strc', 'attr'])
    conc = [[x.split('\t') for x in subconc] for subconc in conc]
    conc = [flatten(x) for x in conc]
    conc = filter(lambda x: x not in [['strc'], ['attr']], conc)
    conc = [filter(None, filter(lambda x: x != '{}', x)) for x in conc]
  return conc


# Convert a raw query result to a flat format (not dependencies etc.).
def cow_raw_to_flat(raw_conc, attrs):
  return [ { 'match_offset' : r['match_offset'], 'match_length' : r['match_length'], 'meta' : r['meta'], 'line' : cow_region_to_conc(r['region'], attrs) } for r in raw_conc]


def cow_print_query(query, file = None, matchmark_left = '', matchmark_right = ''):
  attrs_flag = True if len(query['attributes']) > 1 else False
  conc = cow_raw_to_flat(query['concordance'], attrs_flag)

  handle = open(file, 'w') if file is not None else sys.stdout

  # Write header.
  handle.write('# = BASIC =============================================================\n')
  handle.write('# QUERY:         %s\n' % query['query'])
  handle.write('# CORPUS:        %s\n' % query['corpus'])
  handle.write('# HITS:          %s\n' % query['hits'])
  handle.write('# DATETIME:      %s\n' % query['datetime'])
  handle.write('# ELAPSED:       %s s\n' % str(query['elapsed']))
  handle.write('# = CONFIG ============================================================\n')
  handle.write('# MAX_HITS:      %s\n' % query['max_hits'])
  handle.write('# RANDOM_SUBSET: %s\n' % query['random_subset'])
  handle.write('# ATTRIBUTES:    %s\n' % ','.join(query['attributes']))
  handle.write('# STRUCTURES:    %s\n' % ','.join(query['structures']))
  handle.write('# REFERENCES:    %s\n' % ','.join(query['references']))
  handle.write('# CONTAINER:     %s\n' % query['container'])
  handle.write('# CNT_LEFT:      %s\n' % query['context_left'])
  handle.write('# CNT_RIGHT:     %s\n' % query['context_right'])
  handle.write('# DEDUPING:      %s\n' % query['deduping'])
  handle.write('# DUPLICATES:    %s\n' % query['duplicates'])
  handle.write('# = CONCORDANCE TSV ===================================================\n')

  rex = re.compile('^<.+>$')

  # Write concordance.
  if int(query['hits']) > 1:
    handle.write('\t'.join(query['references'] + ['left.context', 'match', 'right.context']) + '\n')

    for l in conc:

      # Find true tokens via indices (not structs) for separating match from context.
      indices      = [i for i, s in enumerate(l['line']) if not rex.match(s[0])]
      match_start  = indices[l['match_offset']]
      match_end    = indices[l['match_offset'] + l['match_length'] - 1]
      match_length = match_end - match_start + 1

      # Write meta, left, match, right.
      handle.write('\t'.join(l['meta']) + '\t')
      handle.write(' '.join(['|'.join(token) for token in l['line'][:match_start]]) + '\t' + matchmark_right)
      handle.write(' '.join(['|'.join(token) for token in l['line'][match_start:match_end+1]]) + matchmark_left + '\t')
      handle.write(' '.join(['|'.join(token) for token in l['line'][match_end+1:]]) + '\n')

  if handle is not sys.stdout:
      handle.close()

