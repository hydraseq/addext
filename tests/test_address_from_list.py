import csv
import os
import sys
import pytest
sys.path.append(".")
os.chdir("{}/../".format(os.path.dirname(os.path.realpath(__file__))))
from addrext import Sequencer

sequencer = Sequencer()

def _load_column(path_file, column):
    with open(path_file, 'r') as source:
        csv_file = csv.DictReader(source)
        return [row[column] for row in csv_file]

def _load_csv_file(path_file):
    with open(path_file, 'r') as source:
        csv_file = csv.DictReader(source)
    return csv_file


def test_base_addresses():
    base_addresses = _load_column('addrext/data/address/address.csv', 'ADDRESSES')

    for base_address in base_addresses:
        assert sequencer.parse(base_address) == base_address.lower(), '{},"{}"'.format(base_address.lower(), sequencer.encode_from_word_list(sequencer.tokenize_to_list(base_address.lower())))


def test_known_bad_addresses():
    base_addresses = _load_column('addrext/data/known_good/known_bad_addresses.csv', 'ADDRESSES')

    for base_address in base_addresses:
        assert sequencer.parse(base_address.lower()) == '', base_address.lower()

def test_known_good_pobox_addresses():
    poboxs = _load_column('addrext/data/known_good/known_pobox.csv', 'ADDRESSES')

    for pobox in poboxs:
        assert sequencer.parse(pobox) == pobox.lower(), "{} should be a pobox address".format(pobox)

def test_known_good_unique():
    base_addresses = _load_column('addrext/data/known_good/uniques.csv', 'ADDRESSES')

    for base_address in base_addresses:
        assert sequencer.parse(base_address) == base_address.lower(), '{},"{}"'.format(base_address.lower(), sequencer.encode_from_word_list(sequencer.tokenize_to_list(base_address.lower())))


@pytest.mark.skip
def test_known_good_full_clean_addresses():
    base_addresses = _load_column('addrext/data/known_good/full_clean_addresses.csv', 'ADDRESSES')

    for base_address in base_addresses:
        assert sequencer.parse(base_address) == base_address.lower(), '{},"{}"'.format(base_address.lower(), sequencer.encode_from_word_list(sequencer.tokenize_to_list(base_address.lower())))


@pytest.mark.skip
def test_eighty_k_good_street_and_po_samples():
    base_addresses = _load_column('addrext/data/known_good/eighty_k_good_street_and_po_samples.csv', 'ADDRESSES')

    for base_address in base_addresses:
        assert sequencer.parse(base_address) == base_address.lower(), '{},"{}"'.format(base_address.lower(), sequencer.encode_from_word_list(sequencer.tokenize_to_list(base_address.lower())))

