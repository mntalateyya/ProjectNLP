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
		self.sentences = self.setSentences(text)

	# get stored sentences of the text document
	# output: list of sentences
	def getSentences(self):
		return self.sentences

	# set sentences from the text document
	# Notice: supposed to be called once, in initilization
	def setSentences(self, text):
		
		sentences = []

		# Split the text document into sentences (possible annotators: 'tokenize,ssplit,pos,lemma,ner,parse,dcoref')
		output = self.nlp.annotate(text, properties={
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


# ------- example --------

if __name__ == "__main__":
	text = 'Michel Hazanavicius fantasized about making a silent film'

	docObject = Document(text)

	print(docObject.getSentences())


	# Match template pattren to sentence -> generate question accordingly
	# notice: + means one or more, * means 0 or more
	# pattren: proper_noun+ ... verb in the past ... object+ 
	x = docObject.matchTokensRegex(r'([{ tag:"NNP" }])+ []{0,5} ([{ tag:"VBD" }]) []{0,5} ([{ tag:"NN" }])')

	# Sample Template:
	# What [subject] [past verb] about ?
	for matching in x:
		# check if there was a good match
		_subject, _verb, _object = matching['1']['text'], matching['2']['text'] , matching['3']['text']
		question = "What {} {} about?".format(_subject, _verb)
		answer   = _object
		print(question, '- answer:',answer)