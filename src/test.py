#!/usr/bin/python3

from sgraph import SentenceGraph
from pycorenlp import StanfordCoreNLP
from patterns import patterns
import re, pprint
from pattern.en import conjugate

client = StanfordCoreNLP('http://localhost:9000')

with open('data/set1/a2.txt') as f:
    corenlp_out = eval(client.annotate(f.read(), properties={
                'annotators': 'depparse, pos, lemma',
                'corenlp_outputFormat': 'json'
            }))
'''
# from https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
# required if coref used because it returns true and false in lowercase
rep = {"true": "True", "false": "False"} # define desired replacements here
# use these three lines to do the replacement
rep = { re.escape(k): v for k, v in rep.items() }
pattern = re.compile("|".join(rep.keys()))
corenlp_out = eval(pattern.sub(lambda m: rep[re.escape(m.group(0))], corenlp_out))

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(corenlp_out['corefs'])
'''

for sent in corenlp_out['sentences']:
    dg = SentenceGraph(sent)
    res = dg.match(patterns[0])
    if res:
        print('Original: {}'.format(' '.join(map(lambda i: dg.tokens[i]['word'], range(1, dg.length)))))
        print('Q1: Who is ({})? A: ({})'.format(
            dg.subtree(res['subject']), 
            ' '.join(map(lambda i: dg.tokens[i]['word'], range(res['det'], res['pred']+1)))))
        print()
    res = dg.match(patterns[1])
    if res:
        print('Original: {}'.format(' '.join(map(lambda i: dg.tokens[i]['word'], range(1, dg.length)))))
        print('Q2: Who ({})? A: ({})'.format(
            dg.subtree(res['pred']).replace(dg.subtree(res['subject']), ''),
            dg.subtree(res['subject'])))
        print()
    res = dg.match(patterns[2])
    if res is not None and res['time'] < res['verb']:
        print('Original: {}'.format(' '.join(map(lambda i: dg.tokens[i]['word'], range(1, dg.length)))))
        print('Q3: When did ({}) ({}) ({})? A: ({})'.format(
            dg.subtree(res['subject']),
            conjugate(dg.tokens[res['verb']]['word'], 'inf'),
            ' '.join(map(lambda i: dg.tokens[i]['word'], range(res['verb']+1, dg.length-1))),
            dg.subtree(res['time'])
        ))
        print()
        