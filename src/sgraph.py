from functools import reduce
from itertools import chain
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections.abc import Iterable

'''
This module is a dependency graph class. It implements a subset of the semgrex
module of Stanford CoreNLP. Given a pattern that describes a subtree, search for
such a subtree in the dependency parse tree (see patterns.py for pattern syntax).
Also implements subtree which returns the string under a subtree.

Author: Mohammed Nurul Hoque <mnur@cmu.edu> 2018
'''

class SentenceGraph:
    '''
    Store and search in a dependency graph for a single sentence.
    Every prop of self is indexed by token indices and ROOT is stored at index 0 with POS `$`
    '''
    def __init__(self, corenlp_out: Dict[str, Any]):
        '''
        Args:
            corenlp_out: output of corenlp for a sentence as a dictionary
        '''

        self.length = len(corenlp_out['tokens']) + 1
        self.tokens = [{'word': '', 'pos': '$'}] + corenlp_out['tokens']

        self.edges_basic: List[Set[Tuple[str, int]]] = [set() for _ in range(self.length)]
        self.edges_enhanced: List[Set[Tuple[str, int]]] = [set() for _ in range(self.length)]
        for token in corenlp_out['enhancedPlusPlusDependencies']:
            self.edges_enhanced[token['governor']].add((token['dep'], token['dependent']))
        for token in corenlp_out['basicDependencies']:
            self.edges_basic[token['governor']].add((token['dep'], token['dependent']))

    ''' match a pattern on any subtree by iteratively trying to match against each
        node in the tree
    '''
    def match(self, matcher: Dict[str, Any]) -> Optional[Dict[str, int]] :
        for i in range(self.length):
            result = self.find_relation(i, matcher)
            if result is not None:
                return result
    
    ''' return the string of the subtree under a node, ignoring sum relations (see minmax) '''
    def subtree(self, root: int) -> str:
        self.visited = [False for i in range(self.length)]
        low, high = self.minmax(root)
        return ' '.join(map(lambda i: self.tokens[i]['word'], range(low, high+1)))

    ''' lowest index in the subtree '''
    def subtree_start(self, root: int) -> int:
        self.visited = [False for i in range(self.length)]
        return self.minmax(root)[0]
    
    ''' highest index in the subtree '''
    def subtree_end(self, root: int) -> int:
        self.visited = [False for i in range(self.length)]
        return self.minmax(root)[1]

    ''' lowest and highest indices in the subtree, ignores advcl, acl:relcl and punct '''
    def minmax(self, root: int) -> Tuple[int, int] :
        self.visited[root] = True
        minimum, maximum = root, root
        for rel, child in self.edges_basic[root]:
            if rel not in ['acl:relcl', 'advcl', 'punct'] or (rel=='punct' and self.has_root(child)):
                if not self.visited[child]:
                    min_, max_ = self.minmax(child)
                    if min_ < minimum:
                        minimum = min_
                    if max_ > maximum:
                        maximum = max_
        return minimum, maximum

    def has_root(self, root):
        for rel, _ in self.edges_basic[root]:
            if rel == 'root': return True
        return False

    def find_relation(self, root: int, matcher: Dict[str, Any]) -> Optional[Dict[str, int]]:
        '''        
        Args:
            node: node to match against
            matcher: the matching dictionary

        Returns:
            dictionary mapping bound names to their token indices or None if not matched
        '''
        result = {}

        if self.attr_match(root, matcher.get('attributes', {})):
            if 'name' in matcher:
                result[matcher['name']] = root
            for rel_tar, child_matcher in matcher.get('has_deps', {}).items():
            # is this child relation satisfied?
                found = False # false until we find a matching child
                for rel_src, child in chain(self.edges_enhanced[root], self.edges_basic[root]):
                    if rel_src == rel_tar:
                        matched = self.find_relation(child, child_matcher)
                        if matched is not None:
                            found = True
                            result.update(matched)
                            break
                if not found: 
                    return
            for rel_tar in matcher.get('has_not', []):
                for rel_src, _ in chain(self.edges_enhanced[root], self.edges_basic[root]):
                    if rel_src == rel_tar:
                        return
            return result
    
    ''' matches set of attributes against a node '''
    def attr_match(self, node: int, attributes: Dict[str, str]) -> bool:
        for attr, val in attributes.items():
            node_attr = self.tokens[node].get(attr, '$')
            if val[0] == '!':
                choices = map(lambda s: s.strip(), val[1:].split('|'))
                for choice in choices:
                    if node_attr == choice:
                        return False
                return True
            else:
                choices = map(lambda s: s.strip(), val.split('|'))
                for choice in choices:
                    if node_attr == choice:
                        return True
                return False
        return True