"""Compact Drain fixed-depth log parser (self-contained, no external deps).
Ref: He et al., "Drain: An Online Log Parsing Approach with Fixed Depth Tree", ICWS'17.
"""
import re

class LogCluster:
    __slots__ = ('template', 'ids', 'count')
    def __init__(self, template, cid):
        self.template = template      # list of tokens, '<*>' = wildcard
        self.ids = cid
        self.count = 0

class Drain:
    def __init__(self, depth=4, sim_th=0.4, max_child=100):
        self.depth = max(depth, 3) - 2
        self.sim_th = sim_th
        self.max_child = max_child
        self.root = {}
        self.clusters = []
        # preprocessing masks (order matters)
        self.masks = [
            (re.compile(r'(/[-\w./]+)'), '<*>'),                 # paths
            (re.compile(r'\b(0x[0-9a-fA-F]+)\b'), '<*>'),        # hex
            (re.compile(r'\b(\d+\.\d+\.\d+\.\d+)(:\d+)?\b'), '<*>'),  # ip:port
            (re.compile(r'\b[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){3,}\b'), '<*>'),
            (re.compile(r'\b\d+\b'), '<*>'),                     # integers
        ]

    def _preprocess(self, line):
        for pat, rep in self.masks:
            line = pat.sub(rep, line)
        return line.strip().split()

    @staticmethod
    def _seq_dist(tpl, tokens):
        if len(tpl) != len(tokens):
            return -1, 0
        if not tpl:
            return 1.0, 0
        sim = wild = 0
        for t1, t2 in zip(tpl, tokens):
            if t1 == '<*>':
                wild += 1; continue
            if t1 == t2:
                sim += 1
        return sim / len(tpl), wild

    def _tree_search(self, tokens):
        n = len(tokens)
        if n not in self.root:
            return None
        node = self.root[n]
        d = 0
        for tok in tokens:
            if d >= self.depth:
                break
            key = tok if tok != '<*>' else '<*>'
            if key in node:
                node = node[key]
            elif '<*>' in node:
                node = node['<*>']
            else:
                return None
            d += 1
        clusters = node if isinstance(node, list) else node.get('__clusters__', [])
        best, best_sim, best_wild = None, -1, -1
        for c in clusters:
            sim, wild = self._seq_dist(c.template, tokens)
            if sim > best_sim or (sim == best_sim and wild > best_wild):
                best, best_sim, best_wild = c, sim, wild
        if best_sim >= self.sim_th:
            return best
        return None

    def _add(self, tokens):
        n = len(tokens)
        node = self.root.setdefault(n, {})
        d = 0
        for tok in tokens:
            if d >= self.depth:
                break
            key = tok if tok != '<*>' else '<*>'
            if key not in node:
                # limit fanout: collapse to wildcard branch
                if sum(1 for k in node if k != '__clusters__') >= self.max_child:
                    key = '<*>'
                    node = node.setdefault(key, {})
                else:
                    node = node.setdefault(key, {})
            else:
                node = node[key]
            d += 1
        clusters = node.setdefault('__clusters__', [])
        c = LogCluster(list(tokens), len(self.clusters))
        clusters.append(c)
        self.clusters.append(c)
        return c

    def add_line(self, line):
        tokens = self._preprocess(line)
        c = self._tree_search(tokens)
        if c is None:
            c = self._add(tokens)
        else:
            # merge: mark differing positions as wildcard
            merged = ['<*>' if a != b else a for a, b in zip(c.template, tokens)]
            c.template = merged
        c.count += 1
        return c.ids

    def template_str(self, cid):
        return ' '.join(self.clusters[cid].template)
