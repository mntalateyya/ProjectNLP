#!/usr/bin/python3

from depgraph import DepGraph
from utils import Document
from pycorenlp import StanfordCoreNLP

client = StanfordCoreNLP('http://localhost:9000')

with open('/home/mnur/Downloads/Project-Package/data/set1/a2.txt') as f:
    doc = Document(f.read())
print(len(doc.sentences))
for sent in doc.getSentences():
    dg = DepGraph(client, sent)
    res = dg.match('VBD', [('nsubj', None), ('dobj', None)])
    if res:
        verb, subj, obj = res
        #print('Who {} {}? {}'.format(dg.tokens[verb], dg.tokens[obj], dg.tokens[subj]))