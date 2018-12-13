from sys import argv

from pycorenlp import StanfordCoreNLP

from answer_heuris import answer
from maxmatch import maxmatch, sentence2bag
from sgraph import SentenceGraph
from utils import incremental_parse

'''
The driver script which runs the input through the different components.

# Flow
- article document is given to incremental parse to to do coref resolution, returns CoreNLP output
  on the resolved text. (utils.py)
- construct the sentence graph for all these sentences (sgraph.py)
- construct the word bags for all sentences (maxmatch.py)
- 
'''

client = StanfordCoreNLP('http://localhost:9000')

sentences = []
questions = []

document = incremental_parse(client, argv[1], 'depparse, lemma')
sentences = list(map(SentenceGraph, [sentence for prgr in document for sentence in prgr ]))

sentences_bag = list(map(lambda s: sentence2bag(s.tokens), sentences))

with open(argv[2]) as f:
    line = f.readline()
    while line:
        corenlp_out = eval(client.annotate(line, properties={
            'annotators': 'depparse, pos, lemma, ner',
        }))
        questions += corenlp_out['sentences']
        line = f.readline()

questions = list(map(SentenceGraph, questions))

for q in questions:
    print(' '.join(map(lambda tok: tok['word'], q.tokens)))
    ans = answer(sentences, q)
    if ans:
        print(ans.strip())
    else:
        print(maxmatch(sentences, sentences_bag, sentence2bag(q.tokens)))
    print()
