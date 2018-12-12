from pycorenlp import StanfordCoreNLP
import json


# this function finds correference resolution of a text and replaces 
# any entity that is a pronoun with its reference
def correfReplace(text,output):
  sentences = output['sentences']

  # headIndexes: contains entities that contain the same reference
  # headIndexes = {headIndex: (text,position,type)}
  headIndexes = {}
  for n in output['corefs']:
    for l in output['corefs'][n]:
      if l['headIndex'] in headIndexes: 
        headIndexes[l['headIndex']] += [(l['text'],l['position'],l['type'])]
      else: 
        headIndexes[l['headIndex']] = [(l['text'],l['position'],l['type'])]

  # mentionsIndex: this contains the main reference of a headIndex
  # mentionsIndex: {headIndex: text} <= where text is the reference
  mentionsIndex = {}
  for n in headIndexes: 
    for entities in headIndexes[n]: 
      if entities[2] != "PRONOMINAL": 
        mentionsIndex[n] = entities[0]

  # this loop does all the replacing in the sentence
  for n in headIndexes: 
    for entities in headIndexes[n]: 
       # if entity is a pronoun, replace the word
      if entities[2] == "PRONOMINAL":
        sentence_index = entities[1][0]-1
        word_index = entities[1][1]
        sentence = sentences[sentence_index]['tokens']
        for tok in sentence: 
          if tok['index'] == word_index: 
            charoffsetb = tok['characterOffsetBegin']
            charoffsete = tok['characterOffsetEnd']
            before = text[:charoffsetb]
            after = text[charoffsete:]
            ref = mentionsIndex[n]
            text = ref.join((before,after))

  return text


# TEST 

text = "Jack is a football player. He is the best player. He is part of the winning team."

nlp = StanfordCoreNLP('http://localhost:9000')

output = nlp.annotate(text, properties={
      'annotators': 'dcoref', 
      'outputFormat': 'json'
      })

print (correfReplace(text,output))
