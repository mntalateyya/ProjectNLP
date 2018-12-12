from typing import List, Dict
from sgraph import SentenceGraph

name = 'name'
attributes = 'attributes'
has_deps = 'has_deps'
has_not = 'has_not'

def who_is_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    pat1 = { # Who is John? -> John is a player.
        name: 'pred', # the answer
        has_deps: {
            'nsubj': {
                name: 'subject',
                attributes: { 'lemma': question.tokens[res['subject']]['lemma'] }
            },
            'cop': {}
        }
    }

    pat2 = { # Who is the best player? -> John is the best player.
        attributes: { 'lemma': question.tokens[res['subject']]['lemma'] },
        has_deps: {
            rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
            for rel, idx in question.edges_enhanced[res['subject']]
        }
    }
    pat2[has_deps].update({ 'nsubj': { name: 'subject' } }) # answer
    
    for sent in sentences:
        res = sent.match(pat1)
        if res:
            return sent.subtree(res['pred']).replace(sent.subtree(res['subject']), '')
        res = sent.match(pat2)
        if res:
            return sent.subtree(res['subject'])





def who_did_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    0

def when_where_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    0

def why_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    0

patterns = [
    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                attributes: {'lemma': 'who | what'},
                has_deps: {
                    'cop': {},
                    'nsubj': {name: 'subject'}
                }
            }
        }
    },
    who_is_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'nsubj': { attributes: { 'lemma': 'who | what' }}
                }
            }
        }
    },
    who_did_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'nsubjpasss': { attributes: { 'lemma': 'who | what' }}
                }
            }
        }
    },
    who_did_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'dobj': { attributes: { 'lemma': 'who | what' }}
                }
            }
        }
    },
    who_did_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'nmod': { attributes: { 'lemma': 'who | what' }}
                }
            }
        }
    },
    who_did_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: { 'advmod': { attributes: { 'lemma': 'when | where' }}}
            }
        }
    },
    when_where_pat
    ),

    ({
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: { 'advmod': { attributes: { 'lemma': 'why' }}}
            }
        }
    },
    why_pat
    ),
]

def answer(sentences, question):
    for pat, func in patterns:
        res = question.match(pat)
        if res is not None:
            return func(sentences, question, res)
