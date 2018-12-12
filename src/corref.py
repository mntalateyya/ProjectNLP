from pycorenlp import StanfordCoreNLP
import json

# this function finds correference resolution of a text and replaces 
# any entity that is a pronoun with its reference
def correfReplace(text,output):
  sentences = output['sentences']

  # headIndexes: contains entities that contain the same reference
  # headIndexes = {headIndex: (text,sentNum,startIndex,endIndex,type)}
  headIndexes = {}

  for n in output['corefs']:
    for l in output['corefs'][n]:
      if l['headIndex'] in headIndexes: 
        headIndexes[l['headIndex']] += [(l['text'],l['sentNum'],l['startIndex'],l['type'])]
      else: 
        headIndexes[l['headIndex']]  = [(l['text'],l['sentNum'],l['startIndex'],l['type'])]

  # mentionsIndex: this contains the main reference of a headIndex
  # mentionsIndex: {headIndex: text} <= where text is the reference
  mentionsIndex = {}
  for n in headIndexes: 
    for entities in headIndexes[n]: 
      if entities[3] != "PRONOMINAL": 
        mentionsIndex[n] = entities[0]

  possessive = ["his","her","himself","herself","their","its"]

  # this loop does all the replaces in the output (annotated by corenlp)
  for n in headIndexes: 
    for entities in headIndexes[n]: 
       # if entity is a pronoun, replace the word
      if entities[3] == "PRONOMINAL" and n in mentionsIndex:
        sentence_index = entities[1]-1
        word = output['sentences'][sentence_index]['tokens'][entities[2]-1]['word']
        if word in possessive: 
          ref = mentionsIndex[n]+"s"
        else:
          ref = mentionsIndex[n]
        output['sentences'][sentence_index]['tokens'][entities[2]-1]['word'] = ref

  # replaces in the text
  replaced = ""
  for s in range(len(output['sentences'])): 
    for t in range(len(output['sentences'][s]['tokens'])):
      replaced += output['sentences'][s]['tokens'][t]['word']+output['sentences'][s]['tokens'][t]['after']

  return replaced


# TEST 
text = "Jack is a football player. He is the best player. He is part of the winning team."
# output is "Jack is a football player. Jack is the best player. Jack is part of the winning team."

dataf = open("../data/set1/a1.txt","r")
data = dataf.read()

datap = data.split("\n\n")


# since text is too long, I'm giving texts in paragraphs
for text in datap:
  nlp = StanfordCoreNLP('http://localhost:9000')

  output = nlp.annotate(text, properties={
        'annotators': 'dcoref', 
        'outputFormat': 'json'
        })

  print (correfReplace(data,output))

## TEST OUTPUT OF set1/a1 
# He has also played for New England Revolution, Fulham and Tottenham Hotspur. 
# =>
# Dempsey has also played for New England Revolution, Fulham and Tottenham Hotspur.
# -------------------------------------------------------------------------------------------
# He has earned over 100 caps and scored 48 international goals, making him the nation's sixth-most 
# capped player and second top scorer of all time. He has represented the nation at four CONCACAF Gold 
# Cups (winning two), helped them to the final of the 2009 FIFA Confederations Cup and played at three 
# FIFA World Cups, becoming the first American male to score in three World Cups.
# => 
# Dempsey has earned over 100 caps and scored 48 international goals, making Major League Soccer club 
# New England Revolution the nation's sixth-most capped player and second top scorer of all time. Dempsey has 
# represented the nation at four CONCACAF Gold Cups -LRB-winning two-RRB-, helped first to the final of the 2009 
# FIFA Confederations Cup and played at three FIFA World Cups, becoming the first American male to score in three 
# World Cups.
