from functools import reduce
from itertools import chain
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections.abc import Iterable

'''
This module is a dependency graph class. It implements a subset of the semgrex
module of Stanford CoreNLP

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
        self.tokens = [{'word': 'ROOT', 'pos': '$'}] + corenlp_out['tokens']

        self.edges_basic: List[Set[Tuple[str, int]]] = [set() for _ in range(self.length)]
        self.edges_enhanced: List[Set[Tuple[str, int]]] = [set() for _ in range(self.length)]
        for token in corenlp_out['enhancedPlusPlusDependencies']:
            self.edges_enhanced[token['governor']].add((token['dep'], token['dependent']))
        for token in corenlp_out['basicDependencies']:
            self.edges_basic[token['governor']].add((token['dep'], token['dependent']))

    def match(self, matcher: Dict[str, Any]) -> Optional[Dict[str, int]] :
        for i in range(self.length):
            result = self.find_relation(i, matcher)
            if result is not None:
                return result
    
    def subtree(self, root: int) -> str:
        self.visited = [False for i in range(self.length)]
        low, high = self.minmax(root)
        return ' '.join(map(lambda i: self.tokens[i]['word'], range(low, high+1)))
    
    def minmax(self, root: int) -> Tuple[int, int] :
        self.visited[root] = True
        minimum, maximum = root, root
        for rel, child in self.edges_enhanced[root]:
            if rel != 'acl:relcl':
                min_, max_ = self.minmax(child)
                if min_ < minimum:
                    minimum = min_
                if max_ > maximum:
                    maximum = max_
        return minimum, maximum

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
    
    def attr_match(self, node: int, attributes: Dict[str, Union[str, Iterable]]) -> bool:
        for attr, val in attributes.items():
            node_attr = self.tokens[node][attr]
            if type(val) == str:
                if val[0]=='!':
                    if node_attr == val[1:]:
                        return False
                elif node_attr != val:
                    return False
            elif isinstance(val, Iterable):
                match = False
                for choice in val:
                    if node_attr == choice:
                        match = True
                if not match:
                    return False
            else:
                raise TypeError
        return True