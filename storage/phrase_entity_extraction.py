import csv
import os
import re
from hydraseq import Hydraseq
from phrase_entity_encoder import encoder


def w(str_sentence):
    str_sentence = str(str_sentence)
    return re.findall(r"[\w'/\-:#]+|[,!?&]", str_sentence)


# THOU SHALL NOT SEQUENCE THREE ALPHAS IN A ROW!
def train_with_provided_list(seq, matrix_lst):
    """matrix list means [['DIGIT'],['ALPHA'],['WAY']] for example"""
    print(matrix_lst)
    return seq.insert(matrix_lst, is_learning=True).get_next_values()


def train_sequences_from_file(_seq, filepath, lst_lst_identifier):
    """Insert training sequences from stored file.
        _seq    - a live Hydra sequencer to train
        filepath    - csv two column file, second column 'SEQUENCE' contains lists of lists
        lst_lst_identifier  - what identifier to use to cap seqennces, [['mysequence']] for example
    """
    with open(filepath, 'r') as source:
        csv_file = csv.DictReader(source)
        for row in csv_file:
            str_sequence = row['SEQUENCE'].strip()
            if len(str_sequence.strip()) == 0:
                continue
            else:
                lst_sequence = eval(str_sequence)
                train_with_provided_list(_seq, lst_sequence + lst_lst_identifier)


seq = Hydraseq('input')
for typ in ['suite', 'address', 'dir', 'pobox', 'attn']:
    train_sequences_from_file(seq, 'data/address_{}.csv'.format(typ), [['_{}_'.format(typ.upper())]])


def encode_from_word_list(arr_st):
    """Expects ['123', 'main', 'st]"""
    assert isinstance(arr_st, list)
    if arr_st: assert isinstance(arr_st[0], str)
    return [encoder(word) for word in arr_st]

def is_address(seq, arr_st):
    """Expects ["123","main","st"]"""
    return any([pred == '_ADDRESS_' for pred in seq.look_ahead(encode_from_word_list(arr_st)).get_next_values()])

def is_pobox(seq, arr_st):
    """Expects ["123","main","st"]"""
    assert isinstance(arr_st, list)
    return any([pred == '_POBOX_' for pred in seq.look_ahead(encode_from_word_list(arr_st)).get_next_values()])


def is_deleg(seq, arr_st):
    """Expects ["123","main","st"]"""
    assert isinstance(arr_st, list)
    return any([pred == '_ATTN_' for pred in seq.look_ahead(encode_from_word_list(arr_st)).get_next_values()])

def is_suite(seq, st):
    """Expects ["123","main","st"]"""
    assert isinstance(st, str)
    return any([pred == '_SUITE_' for pred in seq.look_ahead(encode_from_word_list(w(st))).get_next_values()])

def get_markers(seq, sent, lst_targets):
    """Input is like '123 main str' and returns a list of lists
        RETURNS: a list of list, each list being a candidate and having these values.
            idx_beg, idx_end, length, matches (ADDRESS etc), sequence
        ATTN!!  this lowercases stuff, TODO: Generalize this so it doesn't need lowercasing
    """
    sent = str(sent).lower().strip()
    arr_w = w(sent)
    idx_tail = len(arr_w)
    markers = []

    for idx_beg in range(idx_tail):
        for idx_end in range(idx_beg + 1, idx_tail +1):
            next_values = seq.look_ahead(encode_from_word_list(arr_w[idx_beg:idx_end])).get_next_values()
            matches = list(set(next_values) & set(lst_targets) )
            if matches:
                markers.append([idx_beg, idx_end, idx_end - idx_beg, matches, ' '.join(arr_w[idx_beg:idx_end])])

    return markers


class BreathFirstSearch:
    """Relies on the structure of nodes to follow the output of get_markers
        [start, end+1, length, [type], str_rep]
    """
    def __init__(self, markers):
        self.markers = markers
    def end(self, node):
        return node[1]
    def start(self, node):
        return node[0]
    def type(self, node):
        return node[3][0]
    def length(self, node):
        return node[2]
    def rep(self, node):
        return node[4]
    def get_successors(self, current_node):
        next_matches = [n for n in self.markers if self.start(n) == self.end(current_node) and self.type(n) != self.type(current_node) and self.type(n) != '_POBOX_']
        return next_matches[:]
    def get_branches(self, node):
        fringe = [[node[:]]]
        branches = []
        while fringe:
            activeNode = fringe.pop()
            successors = self.get_successors(activeNode[-1])
            if successors:
                for successor in successors:
                    nextNode = activeNode[:]
                    nextNode.append(successor)
                    fringe.append(nextNode[:])
            else:
                branches.append(activeNode)
        return branches
    def get_all_branches(self):
        all_branches = []
        for node in self.markers:
            for branch in self.get_branches(node):
                all_branches.append(branch)
        return all_branches



seq2 = Hydraseq('second')
for typ in ['keep']:
    train_sequences_from_file(seq2, 'data/address_{}.csv'.format(typ), [['_{}_'.format(typ.upper())]])

def return_max_address4(seq, sent):

    markers = get_markers(seq, sent, ['_ADDRESS_', '_POBOX_', '_SUITE_', '_DIR_'])
    bfs = BreathFirstSearch(markers)

    keepers = [branch for branch in bfs.get_all_branches() if '_KEEP_' in seq2.look_ahead([node[3] for node in branch] ).get_next_values()]
    max_len = 0
    max_branch = None
    for branch in keepers:
        len_branch = branch[-1][1] - branch[0][0]
        if len_branch > max_len:
            max_len = len_branch
            max_branch = branch

    return " ".join([item[4] for item in max_branch])
