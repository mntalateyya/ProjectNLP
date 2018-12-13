stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as",
             "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]


def sentence2bag(tokenlist):
    result = set()
    for token in tokenlist:
        if token['word'].lower() not in stopwords and token['pos'] != '$':
            result.add(token['lemma'])
    return result


# ------- Maximum Matching using Bag of Words -------- #

# Matching Score is calculated by comparing number of word similarties
# using set() operations
# Args: inputTokensSet: set of tokens, sentenceList: list of set of tokens, each entry represents a sentence
def maximumMatchingSentence(inputTokensSet, sentencesTokensList):
	
	sentenceMatchingScoreList = []

	for sentenceTokensIndex in range(len(sentencesTokensList)):
		sentenceTokens = sentencesTokensList[sentenceTokensIndex]
		entry = (sentenceTokens.intersection(inputTokensSet), sentenceTokens, sentenceTokensIndex)
		sentenceMatchingScoreList.append(entry)

	maximumMatchingSentence = max(sentenceMatchingScoreList)[2]

	return maximumMatchingSentence

def maxmatch(sentences, sentence_bags, question_bag):
    maximal = maximumMatchingSentence(question_bag, sentence_bags)
    return sentences[maximal].subtree(0)