# from https://gist.github.com/sebleier/554280 with some removals
stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
             "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "to", "from", "up", "down", "in", "out", "on", "off", "here", "there", "when", "where", "why", "how", "all", "any", "such", "no", "nor", "not", "so", "than", "too", "very", "s", "t" "just", "don", "should"]


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
        entry = (sentenceTokens.intersection(inputTokensSet),
                 sentenceTokens, sentenceTokensIndex)
        sentenceMatchingScoreList.append(entry)

    maximumMatchingSentence = max(sentenceMatchingScoreList, key=lambda e: len(e[0]))[2]

    return maximumMatchingSentence


''' return the text of the sentence that has the most lexical overlap with the question '''


def maxmatch(sentences, sentence_bags, question_bag):
    maximal = maximumMatchingSentence(question_bag, sentence_bags)
    return ' '.join(map(lambda tok: tok['word'], sentences[maximal].tokens))
