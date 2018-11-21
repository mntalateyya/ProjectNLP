from pycorenlp import StanfordCoreNLP
import json


class Document(object):
	""" 
		Document Class to attach document string, and perform operations
		on it using Stanford CoreNLP Server
	"""
	def __init__(self, text):
		super(Document, self).__init__()
		
		# Get the text document string
		self.string = text

		# Connect to Stanford CoreNLP Server at localhost:9000
		self.nlp = StanfordCoreNLP('http://localhost:9000')

		# Get the sentences from the document string and store them
		self.sentences = self.setSentences()

	# get stored sentences of the text document
	# output: list of sentences
	def getSentences(self):
		return self.sentences

	# set sentences from the text document
	# Notice: supposed to be called once, in initilization
	def setSentences(self):
		
		sentences = []

		# Split the text document into sentences (possible annotators: 'tokenize,ssplit,pos,lemma,ner,parse,dcoref')
		output = self.nlp.annotate(self.string, properties={
		  'annotators': 'ssplit',
		  'outputFormat': 'json'
		 })

		for entry in output['sentences']:
			tokens = entry['tokens']
			if len(tokens) > 0:
				beginIndex = int(tokens[0]['characterOffsetBegin'])
				endIndex   = int(tokens[len(tokens)-1]['characterOffsetEnd'])
				sentences.append(self.string[beginIndex:endIndex])

		return sentences

	# Apply the tokensRegex in all the senteces of the document
	# input: TokensRegex
	# output: list of matchings
	def matchTokensRegex(self, pattern):
		matchings = []

		for sentence in self.getSentences():
			# Since, we are matching one sentence, we expect only one sentence back
			matchingSentence = self.nlp.tokensregex(sentence, pattern=pattern, filter=False)['sentences'][0]
			if matchingSentence['length'] > 0:
				matchings.append(matchingSentence['0'])
		
		return matchings


	# Match templates aganist sentences and apply functions to get the questions
	# input: list of tuples (pattren:string, fn(input): function that takes the matching, then generate the question)
	def generateQuestionsFromPattrens(self, templates):
		questions = []
		for (pattren, questionGenerationFunction) in templates:
			matchings = self.matchTokensRegex(pattren)
			questions.append( questionGenerationFunction(matchings) )
		return questions

# ------- example -------- #

if __name__ == "__main__":
	# ------- Sample Template -------  #
	# What [subject] [past verb] about ?
	# -------------------------------  #
	text = "Hazanavicius fantasized about making a silent film"
	
	def WhatAboutQFn(matchings):
		questions = []
		for matching in matchings:
			# check if there was a match, and generate the question accordingly.
			_subject, _verb, _object = matching['1']['text'], matching['2']['text'] , matching['3']['text']
			question = "What {} {} about?".format(_subject, _verb)
			answer   = _object
			questions.append(question)
		return (" ".join(questions))

	# Read the document as ASCII text, and ignore unicode symbols
	sampleDocObj = Document(text)

	# Match template pattren to sentence -> generate question accordingly
	# Notice: + means one or more, * means zero or more
	# pattren: proper_noun+ ... verb in the past tense ... object+ 
	sampleTemplate = (r'([{ tag:"NNP" }]) []{0,5} ([{ tag:"VBD" }]) []{0,5} ([{ tag:"NN" }])', WhatAboutQFn)

	# output: ['What Hazanavicius fantasized about?']
	print(sampleDocObj.generateQuestionsFromPattrens([sampleTemplate]))