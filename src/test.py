#!/usr/bin/python3

from sgraph import SentenceGraph
from pycorenlp import StanfordCoreNLP
from patterns import patterns
from sys import argv
# import re, pprint

client = StanfordCoreNLP('http://localhost:9000')

for fname in argv[1:]:
    with open(fname) as f:
        corenlp_out = eval(client.annotate(f.read(), properties={
                    'annotators': 'depparse, pos, lemma, ner    ',
                    'corenlp_outputFormat': 'json'
                }))

    for sent in corenlp_out['sentences']:
        sg = SentenceGraph(sent)
        for i, (pat, tmpl) in enumerate(patterns):
            res = sg.match(pat)
            if res is not None:
                q = tmpl(sg, res)
                if q[0]:
                    print('Original:', ' '.join(map(lambda i: sg.tokens[i]['word'], range(1, sg.length))))
                    print('Q[{}]:'.format(i), q[0], '\n', 'A:', q[1])
                    print()

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