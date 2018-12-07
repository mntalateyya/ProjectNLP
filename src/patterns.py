from pattern.en import conjugate
'''
List of pattern-template tuples. A pattern matches nodes in the dependency graph
and is a dictionary that has zero or more of the following 4 keys:
- name: if successfully matched the returned dictionary will have this as a key mapping
        to the index of this node.
- attributes: a dictionary of attributes this node has to have. these attributes are the
        token attrubutes in CoreNLP output. e.g. `'attributes': { 'pos': 'NNP' }`. The attribute
        value can also be '!value' in which case, it matches anything but value and can also be
        a set (or list, prefer set), in which case it matches if one of
        the values match. `'attributes': { 'pos': { 'VBD', 'VBN' }}` (!value not permitted here).
- 'has_deps': depndency relations this node should have, where this node is the governor
        of the relation. This a dictionary where keys are relations and values are 
        recursive patterns.
- 'has_not': a list of relations this node should not have.
'''
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
                'attributes': {'pos': 'NNP'}
            },
        }
    },
    lambda sg, res: (
        'Who is {}?'.format(sg.subtree(res['subject'])),
        'A: {}'.format(' '.join(
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
                'name': 'subject'
            },
        }
    },
    lambda sg, res: (
        'Who {}?'.format(sg.subtree(res['pred']).replace(
            sg.subtree(res['subject']), '')),
        'A: {}'.format(sg.subtree(res['subject']))
    )),

    ({
        'name': 'verb',
        'attributes': {'pos': 'VBD'},
        'has_deps': {
            'nmod:in': {'name': 'time'},
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
        ) if res['time'] < res['verb'] else '',
        'A: {}'.format(sg.subtree(res['time']))
    )),
]
