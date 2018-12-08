from pattern.en import conjugate
'''
List of pattern-template tuples. 

A pattern matches nodes in the dependency graph and is a dictionary that has zero or more
of the following 4 keys:
- name: if successfully matched the returned dictionary will have this as a key mapping
        to the index of this node.
- attributes: a dictionary of attributes this node has to have. these attributes are the
        token attrubutes in CoreNLP output. e.g. `'attributes': { 'pos': 'NNP' }`. The attribute
        value is of the form `var1 | ... | varn` which matches if any of the varients match.
        Alternatively, it can be `! var1 | ... | varn` which matches if none of the varients match.
- 'has_deps': depndency relations this node should have, where this node is the governor
        of the relation. This a dictionary where keys are relations and values are 
        recursive patterns.
- 'has_not': a list of relations this node should not have.

a template is a function that takes the SentenceGraph object and result of matching and generates
a question-answer pair of strings. The answer is only for our testing so return an empty string if
you wish.
'''

def bc_pattern(sg, res): 
    v_tok = sg.tokens[res['verb']]
    if v_tok['pos'] == 'VBN':
        aux = sg.tokens[res['aux']]['word']
    else:
        aux = { 'VBD': 'did', 'VBP': 'do', 'VBZ': 'does' }[v_tok['pos']]
    verb = v_tok['word'] if v_tok['pos'] == 'VBN' else conjugate(v_tok['word'], 'inf')
    clause = ' '.join(map(lambda i: sg.tokens[i]['word'], range(res['verb']+1, sg.subtree_start(res['reason']))))
    return (
        'Why {} {} {} {}?'.format(aux, sg.subtree(res['subject']), verb, clause),
        '{}'.format(sg.subtree(res['reason']))
    )

patterns = [
    ({
        'name': 'pred',
        'has_deps': {
            'det': {
                'name': 'det',
                'attributes': {'word': 'a'}},
            'cop': {'attributes': {'word': 'is'}},
            'nsubj': {
                'name': 'subject',
                'attributes': {'ner': 'PERSON'}
            },
        }
    },
    lambda sg, res: (
        'Who is {}?'.format(sg.subtree(res['subject'])),
        '{}'.format(' '.join(
            map(lambda i: sg.tokens[i]['word'], range(res['det'], res['pred']+1))))
    )),

    ({
        'name': 'pred',
        'has_deps': {
            'det': {
                'name': 'det',
                'attributes': {'word': 'a'}},
            'cop': {'attributes': {'word': 'is'}},
            'nsubj': {
                'name': 'subject',
                'attributes': {'ner': '! PERSON | O'}
            },
        }
    },
    lambda sg, res: (
        'What is {}?'.format(sg.subtree(res['subject'])),
        '{}'.format(' '.join(
            map(lambda i: sg.tokens[i]['word'], range(res['det'], res['pred']+1))))
    )),

    ({
        'name': 'pred',
        'has_deps': {
            'det': {
                'name': 'det',
                'attributes': {'word': 'the'}},
            'cop': {'attributes': {'word': 'is'}},
            'nsubj': {
                'name': 'subject',
                'attributes': {'ner': 'PERSON'}
            },
        }
    },
    lambda sg, res: (
        'Who {}?'.format(sg.subtree(res['pred']).replace(
            sg.subtree(res['subject']), '')),
        '{}'.format(sg.subtree(res['subject']))
    )),

    ({
        'name': 'pred',
        'has_deps': {
            'det': {
                'name': 'det',
                'attributes': {'word': 'the'}},
            'cop': {'attributes': {'word': 'is'}},
            'nsubj': {
                'name': 'subject',
                'attributes': {'ner': '! PERSON | O'}
            },
        }
    },
    lambda sg, res: (
        'What {}?'.format(sg.subtree(res['pred']).replace(
            sg.subtree(res['subject']), '')),
        '{}'.format(sg.subtree(res['subject']))
    )),

    ({
        'name': 'verb',
        'attributes': {'pos': 'VBD'},
        'has_deps': {
            'nmod:in': {'name': 'time', 'attributes': {'ner': 'DATE'}},
            'nsubj': {'name': 'subject', 'attributes': {'pos': '!PRP'}}
        },
        'has_not': ['cc']
    },
    lambda sg, res: (
        'When did {} {} {}?'.format(
            sg.subtree(res['subject']),
            conjugate(sg.tokens[res['verb']]['word'], 'inf'),
            ' '.join(map(lambda i: sg.tokens[i]['word'], range(
                res['verb']+1, sg.length-1)))
        ) if sg.subtree_start(res['time']) == 1 else '',
        '{}'.format(sg.subtree(res['time']))
    )),

    # FIXME catched verbs not modified with in, e.g. 
    # In 2005 , after six years with the club , the majority of which were spent on 
    # loan at the San Jose Earthquakes , Donovan moved tothe Los Angeles Galaxy .
    # NOTE the error is actually caused by parse error by CoreNLP.
    ({
        'name': 'verb',
        'attributes': { 'pos': 'VBN' },
        'has_deps': {
            'nmod:in': { 'name': 'time', 'attributes': {'ner': 'DATE'}},
            'auxpass': { 'name': 'aux' },
            'nsubjpass': { 'name': 'subject', 'attributes': { 'pos': '!PRP' }}
        },
    },
    lambda sg, res: (
        'When {} {} {}?'.format(
            sg.subtree(res['aux']),
            sg.subtree(res['subject']),
            ' '.join(map(lambda i: sg.tokens[i]['word'], range(res['verb'], sg.length-1)))
        ) if sg.subtree_start(res['time']) == 1 else '',
        '{}'.format(sg.subtree(res['time']))
    )),

    ({
        'name': 'verb',
        'attributes': { 'pos': 'VBD | VBP | VBZ' },
        'has_deps': {
            'nsubj': { 'name': 'subject' },
            'advcl:because': { 'name': 'reason' }
        }
    },
    lambda sg, res: bc_pattern(sg, res)
    ),

    ({
        'name': 'verb',
        'attributes': { 'pos': 'VBN' },
        'has_deps': {
            'nsubjpass': { 'name': 'subject' },
            'advcl:because': { 'name': 'reason' },
            'auxpass': { 'name': 'aux' }
        }
    },
    lambda sg, res: bc_pattern(sg, res)
    )
]