from pycorenlp import StanfordCoreNLP
import json

# this function finds correference resolution of a text and replaces 
# any entity that is a pronoun with its reference
def correfReplace(text,output):
  sentences = output['sentences']

  for n in output['corefs']:

    # headIndexes: contains entities that contain the same reference
    # headIndexes = {headIndex: (text,sentNum,startIndex,endIndex,type)}
    headIndexes = {}

    for l in output['corefs'][n]:
      if l['headIndex'] in headIndexes: 
        headIndexes[l['headIndex']] += [(l['text'],l['sentNum'],l['startIndex'],l['type'])]
      else: 
        headIndexes[l['headIndex']]  = [(l['text'],l['sentNum'],l['startIndex'],l['type'])]

    # mentionsIndex: this contains the main reference of a headIndex
    # mentionsIndex: {headIndex: text} <= where text is the reference
    mentionsIndex = {}
    for n1 in headIndexes: 
      for entities in headIndexes[n1]: 
        if entities[3] != "PRONOMINAL": 
          mentionsIndex[n1] = entities[0]

    possessive = ["his","her","himself","herself","their","its"]

    # this loop does all the replaces in the output (annotated by corenlp)
    for n2 in headIndexes: 
      for entities in headIndexes[n2]: 
         # if entity is a pronoun, replace the word
        if entities[3] == "PRONOMINAL" and n2 in mentionsIndex:
          sentence_index = entities[1]-1
          word = output['sentences'][sentence_index]['tokens'][entities[2]-1]['word']
          if word in possessive: 
            ref = mentionsIndex[n2]+"s"
          else:
            ref = mentionsIndex[n2]
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

text = "Jack is a football player. He is the best player. He is part of the winning team. Mina is a student. She hates coffee."
# output is "Jack is a football player. Jack is the best player. Jack is part of the winning team. Mina is a student. Mina hates coffee."


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
#
# Clinton Drew "Clint" Dempsey /ˈdɛmpsi/ (born March 9, 1983) is an American professional 
# soccer player who plays for Seattle Sounders FC in Major League Soccer and has served as 
# the captain of the United States national team. He has also played for New England 
# Revolution, Fulham and Tottenham Hotspur.
# Growing up in Nacogdoches, Texas, Dempsey played for one of the top youth soccer clubs 
# in the state, the Dallas Texans, before playing for Furman University's men's soccer team. 
# In 2004, Dempsey was drafted by Major League Soccer club New England Revolution, where he 
# quickly integrated himself into the starting lineup. Hindered initially by a jaw injury, 
# he would eventually score 25 goals in 71 appearances with the Revolution. Between 2007 and 
# 2012, Dempsey played for Premier League team Fulham and is the club's highest Premier 
# League goalscorer of all time. Dempsey became the first American player to score a 
# hat-trick in the English Premier League, in the 5–2 win over Newcastle United in January 
# 2012.
#
# =>
#    
# Clinton Drew ``Clint'' Dempsey /ˈdɛmpsi/ -LRB-born March 9, 1983-RRB- is an American 
# professional soccer player who plays for Seattle Sounders FC in Major League Soccer and has 
# served as the captain of the United States national team. Dempsey has also played for New 
# England Revolution, Fulham and Tottenham Hotspur.
# Growing up in Nacogdoches, Texas, Dempsey played for one of the top youth soccer clubs in 
# the state, the Dallas Texans, before playing for Furman University's men's soccer team. In 
# 004, Dempsey was drafted by Major League Soccer club New England Revolution, where he 
# quickly integrated himself into the starting lineup. Hindered initially by a jaw injury, 
# Dempsey would eventually score 25 goals in 71 appearances with the Revolution. Between 2007 
# nd 2012, Dempsey played for Premier League team Fulham and is the club's highest Premier 
# League goalscorer of all time. Dempsey became the first American player to score a 
# hat-trick in the English Premier League, in the 5--2 win over Newcastle United in January 
# 2012.
