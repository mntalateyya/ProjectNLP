'''
This module is a dependency graph class. It implements a subset of the semgrex
module of Stanford CoreNLP

Author: Mohammed Nurul Hoque <mnur@cmu.edu> 2018
'''
class DepGraph:
    '''
    Store and search in a dependency graph and POS tags for a single sentence.
    Every prop of self is indexed by word indices and ROOT is stored at index length
    '''
    def __init__(self, corenlp_client, sentence):
        '''
        Args:
            corenlp_client: client object
            sentence: sentence to parse and search in
        '''

        out = corenlp_client.annotate(sentence, properties={
            'annotators': 'depparse, pos',
            'outputFormat': 'json'
        })['sentences'][0]

        self.length = len(out['tokens'])

        self.tokens = ['ROOT'] + list(map(lambda tok: tok['word'], out['tokens']))
        self.pos = ['$'] + list(map(lambda tok: tok['pos'], out['tokens']))
        self.edges = [set() for _ in range(len(out['tokens'])+1)]

        for token in out['enhancedPlusPlusDependencies']:
            self.add_dep(token['governor'], token['dependent'], token['dep'])

    def add_dep(self, parent, child, relation):
        ''' add the relation from parent word index to child word index '''
        self.edges[parent].add((child, relation))

    def find_relation(self, node, parent_pos, children):
        '''
        Args:
            node: index of node to search under (searches the subtree rooted at node)
            parent_pos: the required parent POS or None if unspecified
            children: an iterable that yields (relation, pos) constraints for children, pos is
            allowed to be None for unspecified pos
        '''

        found = False
        if not parent_pos or (self.pos[node] == parent_pos):
            result = [node]
            found = True
            for rel_target, pos in children:
                found = False
                for child, rel_source in self.edges[node]:
                    if (rel_source == rel_target) and (not pos or (self.pos[child] == pos)):
                        found = True
                        result.append(child)
                        break
                if not found:
                    break
        if found:
            return result

        for child, _ in self.edges[node]:
            result = self.find_relation(child, parent_pos, children)
            if result:
                return result
        return []
