from typing import List, Dict
from copy import deepcopy
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

def who_did_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int], rel: str):
    pat = {
        attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
        has_deps: {
            rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
            for rel, idx in question.edges_enhanced[res['root']] if rel in ['nsubj', 'nsubjpass', 'dobj', 'iobj']
        }
    }
    if rel == 'nmod':
        rel += ':{}'.format(question.tokens[res['prep']]['lemma'])
    pat[has_deps].update({rel: {'name': 'subject' }})

    pat2 = deepcopy(pat)
    pat2[has_deps].pop(rel)
    pred_dep = {'nsubj': 'csubj', 'nsubjpass': 'csubjpass', 'dobj': 'ccomp', 'iobj': 'ccomp'}
    pat2[has_deps].update({pred_dep[rel]: {'name': 'subject' }})

    for sent in sentences:
        res = sent.match(pat)
        if res:
            return sent.subtree(res['subject'])
        res = sent.match(pat2)
        if res:
            return sent.subtree(res['subject'])


    

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

    ({ # who did <sth>
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
    lambda s, q, r: who_did_pat(s, q, r, 'nsubj')
    ),

    ({ # who was done <sth>, e.g 
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'nsubjpass': { attributes: { 'lemma': 'who | what' }}
                }
            }
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'nsubjpass')
    ),

    ({ # Who did <sth> do, e.g Who did John meet, What did John eat
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'dobj': { attributes: { 'lemma': 'who | what | whom' }}
                }
            }
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'dobj')
    ),

    ({ # Who did <sth> do, e.g Who did John meet, What did John eat
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'iobj': { attributes: { 'lemma': 'who | what | whom' }}
                }
            }
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'iobj')
    ),

    ({ # Who was sth done by/with/.., e.g Who was London built by
        attributes: {'pos': '$'},
        has_deps: {
            'ROOT': {
                name: 'root',
                has_deps: {
                    'nmod': {
                        attributes: { 'lemma': 'who | what' },
                        has_deps: { 'case': { name: 'prep' }}
                    }
                }
            }
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'nmod')
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
