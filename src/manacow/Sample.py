# -*- coding: utf-8 -*-

from ManaCOW import cow_query, cow_print_query

query = cow_query('"Chuzpe"', corpus = 'decow16a-nano', references = ['doc.url', 's.type'],
  attributes = ['word', 'tag'], structures = ['s'], deduping = True, max_hits = 2)

cow_print_query(query)
