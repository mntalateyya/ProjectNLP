from typing import List, Dict
from copy import deepcopy
from sgraph import SentenceGraph

name = 'name'
attributes = 'attributes'
has_deps = 'has_deps'
has_not = 'has_not'

# Capitalize the first letter, add punctuation.
def prettify(sentence: str) -> str: 
    return sentence[0].upper() + sentence[1:] + "."


def who_is_pat(sentences: List[SentenceGraph], question: SentenceGraph, res: Dict[str, int]):
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
                .replace(cop, '', 1))
        res = sent.match(pat2)
        if res:
            return sent.subtree(res['subject'])

def who_did_pat(sentences: List[SentenceGraph], question: List[SentenceGraph], res: Dict[str, int], rel: str):
    pats = [{
        attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
        has_deps: {
            rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
            for rel, idx in question.edges_enhanced[res['root']] 
            if rel in ['nsubj', 'nsubjpass', 'dobj', 'iobj', 'amod', 'advmod'] or rel[:4] == 'nmod'
        }
    }]
    if rel == 'nmod':
        rel += ':{}'.format(question.tokens[res['prep']]['lemma'])
    pats[0][has_deps].update({rel: {'name': 'subject' }})

    pat = deepcopy(pats[0])
    pat[has_deps].pop(rel)
    pred_dep = {'nsubj': 'csubj', 'nsubjpass': 'csubjpass', 'dobj': 'ccomp', 'iobj': 'ccomp'}
    pat[has_deps].update({pred_dep[rel]: {'name': 'subject' }})
    pats.append(pat)

    if rel in ['nsubj', 'nsubjpass']:
        flip = {'nsubj': 'nsubjpass', 'nsubjpass': 'nsubj'}[rel]
        pat = deepcopy(pats[0])
        pat[has_deps].pop(rel)
        pat[has_deps].update({flip: {'name': 'subject' }})
        pats.append(pat)
    
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
        } for rel in ['nmod:in', 'nmod:tmod'] # NOTE add others
    ]
    for sent in sentences:
        for pat in pats:
            res = sent.match(pat)
            if res:
                return sent.subtree(res['spacetime'])

def how_many_pat(sentences, question, res):
    pats = [
        {
            name: 'root',
            attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
            has_deps: {
                'nummod': {}
            }
        },
        {
            name: 'root',
            attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
            has_deps: {
                'amod:qmod': {}
            }
        },
        {
            name: 'root',
            has_deps: {
                'nmod:of': { attributes: { 'lemma': question.tokens[res['root']]['lemma'] } }
            }
        }
    ]

    for sent in sentences:
        for pat in pats:
            res = sent.match(pat)
            if res:
                return sent.subtree(res['root'])

def why_pat(sentences: List[SentenceGraph], question: SentenceGraph, res: Dict[str, int]):
    pat = { # John eats because he was hungry.
        name: 'pred', # the verb
        attributes: {'lemma': question.tokens[res['root']]['lemma']},
        has_deps: {
            'advcl:because': {
                name: 'reason'
            },
            'nsubj': { 
                name: 'subject',
                attributes: {'lemma': question.tokens[res['subject']]['lemma']}
            }
        }
    }

    pat2 = { # John eats so that he prevents his hunger.
        name: 'pred', # the verb
        attributes: {'lemma': question.tokens[res['root']]['lemma']},
        has_deps: {
            'advcl:so_that': {
                name: 'reason'
            },
            'nsubj': { 
                name: 'subject',
                attributes: {'lemma': question.tokens[res['subject']]['lemma']}
            }
        }
    }

    pat3 = { # John eats to satisfy himself.
        name: 'pred', # the verb
        attributes: {'lemma': question.tokens[res['root']]['lemma']},
        has_deps: {
            'xcomp': {
                name: 'reason',
                has_deps: {
                    'mark': {
                        attributes: {'lemma': "to"}
                    }
                }
            },
            'nsubj': { 
                name: 'subject',
                attributes: {'lemma': question.tokens[res['subject']]['lemma']}
            }
        }
    }

    pat4 = { # John eats in order to prevent his hunger.
        name: 'pred', # the verb
        attributes: {'lemma': question.tokens[res['root']]['lemma']},
        has_deps: {
            'advcl:in_order': {
                name: 'reason'
            },
            'nsubj': { 
                name: 'subject',
                attributes: {'lemma': question.tokens[res['subject']]['lemma']}
            }
        }
    }

    pats_extra = [
        {
            attributes: { 'lemma': question.tokens[res['root']]['lemma'] },
            has_deps: {
                **{
                    rel: { attributes: { 'lemma': question.tokens[idx]['lemma'] }} 
                    for rel, idx in question.edges_enhanced[res['root']] 
                    if rel in ['nsubj', 'nsubjpass', 'dobj', 'iobj', 'amod']
                },
                rel: { name: 'reason' },
            }
        } for rel in ['nmod:because', 'nmod:because_of', 'advcl:to']
    ]
    
    for sent in sentences:
        res = sent.match(pat)
        if res:
            return sent.subtree(res['reason'])
        res = sent.match(pat2)
        if res:
            return sent.subtree(res['reason'])
        res = sent.match(pat3)
        if res:
            reason_subtree = dict(sent.edges_enhanced[res["reason"]])
            reason_start = reason_subtree['mark']
            reason_end = sent.subtree_end(res['reason'])+1
            return ' '.join(token['word'] for token in sent.tokens[reason_start:reason_end])
        res = sent.match(pat4)
        if res:
            return sent.subtree(res['reason'])
        for pat in pats_extra:
            res = sent.match(pat)
            if res:
                return sent.subtree(res['reason'])


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
        name: 'root',
        has_deps: { 'advmod': { attributes: { 'lemma': 'why' }}}

    },
    why_pat
    ),

    ({
        name: 'root',
        has_deps: {
            'amod': {
                name: 'quantity',
                has_deps: { 
                    'advmod': { attributes: { 'lemma': 'how' }}
                }
            }
        }
    }, how_many_pat)
]

def answer(sentences, question):
    for pat, func in patterns:
        res = question.match(pat)
        if res is not None:
            answer = func(sentences, question, res)
            if answer is not None:
                return prettify(answer)
