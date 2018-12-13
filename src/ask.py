#!/usr/bin/python3
from sys import argv, stderr
from sgraph import SentenceGraph
from pycorenlp import StanfordCoreNLP
from patterns import patterns
from utils import incremental_parse

filename = argv[1]
n = int(argv[2])

client = StanfordCoreNLP('http://localhost:9000')

questions = {}
# is first sentence in paragraph, for higher ranking
newsection = True

document = incremental_parse(client, filename, 'depparse, pos, lemma, ner')
for paragraphs in document:
    for i, sentence in enumerate(paragraphs):
        sg = SentenceGraph(sentence)
        for (pat, tmpl) in patterns:
            res = sg.match(pat)
            if res is not None:
                q, _ = tmpl(sg, res)
                if q:
                    if i == 0:
                        questions[q] = 5
                    else:
                        questions[q] = 1

qlist = sorted(questions.items(), key=lambda item: item[1]/len(item[0].split())**0.5, reverse=True)
for i in range(min(n, len(qlist))):
    print('[{}]- '.format(i+1), qlist[i][0], qlist[i][1])

if n > len(qlist):
    stderr.write('\033[01;31m'+'Only {} questions were generated\n'.format(len(qlist)))