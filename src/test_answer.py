#!/usr/bin/python3
from sys import argv
from pycorenlp import StanfordCoreNLP
from answer_heuris import answer
from sgraph import SentenceGraph

#with open(argv[1]) as f:
#    text = f.readline()

text = 'John is the best football player. John likes apples. John ate to relieve his hunger. John met Jane yesterday. John ate with Jane. John was killed.'

questions = [
    'Who is John?',
    'Who is the best football player?',
    'Who likes apples?',
    'Who did John meet?',
    'Who did John eat with?',
    'Why did John eat?'
    #'Who was killed?'
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
