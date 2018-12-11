#!/usr/bin/python3
from sys import argv, stderr
from sgraph import SentenceGraph
from pycorenlp import StanfordCoreNLP
from patterns import patterns

filename = argv[1]
n = int(argv[2])

client = StanfordCoreNLP('http://localhost:9000')

questions = {}
newpar = True

with open(filename) as f:
    line = f.readline()
    while line:
        if (line.strip() == ''):
            newpar = True
        if len(line) < 60:
            line = f.readline()
            continue
        corenlp_out = eval(client.annotate(line, properties={
                'annotators': 'depparse, pos, lemma, ner',
            }))
        for sent in corenlp_out['sentences']:
            sg = SentenceGraph(sent)
            for i, (pat, tmpl) in enumerate(patterns):
                res = sg.match(pat)
                if res is not None:
                    q, _ = tmpl(sg, res)
                    if q:
                        questions[q] = 10 if newpar else 1
        newpar = False
        line = f.readline()

qlist = sorted(questions.items(), key=lambda item: item[1], reverse=True)
for i in range(min(n, len(qlist))):
    print('[{}]- '.format(i+1), qlist[i][0])

if n > len(qlist):
    stderr.write('\033[01;31m'+'Only {} questions were generated\n'.format(len(qlist)))


        