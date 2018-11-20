#!/usr/bin/python3

from depgraph import DepGraph
from pycorenlp import StanfordCoreNLP

client = StanfordCoreNLP('http://localhost:9000')

sents = ['Linus created Linux', 'You ate the apple', 'I wrote a book']
for sent in sents:
    dg = DepGraph(client, sent)
    verb, subj, obj = dg.find_relation(0, 'VBD', [('nsubj', None), ('dobj', None)])
    print('Who {} {}? {}'.format(dg.tokens[verb], dg.tokens[obj], dg.tokens[subj]))