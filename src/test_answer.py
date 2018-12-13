#!/usr/bin/python3
from sys import argv
from pycorenlp import StanfordCoreNLP
from answer_heuris import answer
from sgraph import SentenceGraph


# with open(argv[1]) as f:
    # text = f.read()
text = 'There are three boxes of spoons.'
text += ''
questions = [
    # 'What does the modern symbol for Cancer represent?',
    # 'Who set out the official official constellation boundaries of Cancer?',
    # 'In Chinese astronomy, what does the stars of Cancer lie within?',
    # 'What is the dimmest of zodiacal constellations?',
    # 'What is located at the center of Cancer\'s constellation?',
    # 'What is the brightest star in Cancer?',
    # 'What is cancer?',
    # 'What is one of the closest open clusters to Earth? ',
    # 'What is Iota Cancri? ',
    'How many spoons are there?',
    # 'What borders Cancer to the west?',
    # 'When is Cancer best visible?'
]

client = StanfordCoreNLP('http://localhost:9000')

sentences =  corenlp_out = eval(client.annotate(text, properties={
    'annotators': 'depparse, lemma',    
}))['sentences']
sentences = list(map(SentenceGraph, sentences))

parse_questions = [
    SentenceGraph(
        eval(client.annotate(q, properties={ 'annotators': 'depparse, lemma' }))['sentences'][0]
    ) for q in questions
]

for i, q in enumerate(parse_questions):
    ans = answer(sentences, q)
    print(questions[i])
    print(ans if ans else 'NOT FOUND')
    print()
