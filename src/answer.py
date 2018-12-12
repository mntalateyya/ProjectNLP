from sys import argv
from pycorenlp import StanfordCoreNLP
from answer_heuris import answer
from maxmatch import maxmatch, sentence2bag
from sgraph import SentenceGraph

client = StanfordCoreNLP('http://localhost:9000')

sentences = []
questions = []

with open(argv[1]) as f:
    line = f.readline()
    while line:
        if len(line) < 48:
            line = f.readline()
            continue
        corenlp_out = eval(client.annotate(line, properties={
                'annotators': 'depparse, lemma',
            }))
        sentences += corenlp_out['sentences']
        line = f.readline()
sentences = list(map(SentenceGraph, sentences))
#sentences_text = [s.subtree(0) for s in sentences]

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