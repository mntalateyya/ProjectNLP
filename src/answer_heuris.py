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
    
    cop = question.tokens[res['cop']]['word']

    for sent in sentences:
        res = sent.match(pat1)
        if res:
            return (sent.subtree(res['pred'])
                .replace(sent.subtree(res['subject']), '')
                .replace(cop, '', 1)).strip()
        res = sent.match(pat2)
        if res:
            return sent.subtree(res['subject'])

def who_did_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int], rel: str):
    pats = [{
        attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
        has_deps: {
            rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
            for rel, idx in question.edges_enhanced[res['root']] 
            if rel in ['nsubj', 'nsubjpass', 'dobj', 'iobj', 'amod', 'advmod']
        }
    }]
    if rel == 'nmod':
        rel += ':{}'.format(question.tokens[res['prep']]['lemma'])
    pats[0][has_deps].update({rel: {'name': 'subject' }})

    pat2 = deepcopy(pats[0])
    pat2[has_deps].pop(rel)
    pred_dep = {'nsubj': 'csubj', 'nsubjpass': 'csubjpass', 'dobj': 'ccomp', 'iobj': 'ccomp'}
    pat2[has_deps].update({pred_dep[rel]: {'name': 'subject' }})
    pats.append(pat2)
    
    for sent in sentences:
        for pat in pats:
            res = sent.match(pat)
            if res:
                return sent.subtree(res['subject'])

def when_where_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    pats = [
        {
            attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
            has_deps: {
                **{
                    rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
                    for rel, idx in question.edges_enhanced[res['root']] 
                    if rel in ['nsubj', 'nsubjpass', 'dobj', 'iobj', 'amod']
                },
                rel: { name: 'spacetime' },
            }
        } for rel in ['nmod:in', 'nmod:tmod', 'advmod'] # NOTE add others
    ]
    for sent in sentences:
        for pat in pats:
            res = sent.match(pat)
            if res:
                return sent.subtree(res['spacetime'])

def why_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int]):
    0

patterns = [
    ({
        attributes: {'lemma': 'who | what'},
        has_deps: {
            'cop': { name: 'cop' },
            'nsubj': {name: 'subject'}
        }
    },
    who_is_pat
    ),

    ({
        name: 'root',
        has_deps: {
            'nsubj': { attributes: { 'lemma': 'who | what' }}
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'nsubj')
    ),

    ({
        name: 'root',
        has_deps: {
            'nsubjpass': { attributes: { 'lemma': 'who | what' }}
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'nsubjpass')
    ),

    ( {
        name: 'root',
        has_deps: {
            'dobj': { attributes: { 'lemma': 'who | what | whom' }}
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'dobj')
    ),

    ({
        name: 'root',
        has_deps: {
            'iobj': { attributes: { 'lemma': 'who | what | whom' }}
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'iobj')
    ),

    ({
        name: 'root',
        has_deps: {
            'nmod': {
                attributes: { 'lemma': 'who | what' },
                has_deps: { 'case': { name: 'prep' }}
            }
        }
    },
    lambda s, q, r: who_did_pat(s, q, r, 'nmod')
    ),

    ({
        name: 'root',
        has_deps: { 'advmod': { attributes: { 'lemma': 'when | where' }}}
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
