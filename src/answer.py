from sys import argv
from pycorenlp import StanfordCoreNLP
from answer_heuris import answer
from maxmatch import maxmatch, sentence2bag
from sgraph import SentenceGraph
from utils import incremental_parse
client = StanfordCoreNLP('http://localhost:9000')

sentences = []
questions = []

document = incremental_parse(client, argv[1], 'depparse, lemma')
sentences = list(map(SentenceGraph, [sentence for sentence in prgr for prgr in document]))

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
    ans = answer(sentences, q)
    if ans:
        print(ans)
    else:
        print(maxmatch(sentences, sentences_bag, sentence2bag(q.tokens)))