#! /usr/bin/env python3
"""
Convert a german Volksbank cash account csv file to homebank-readable csv format
"""

import argparse
import csv
from datetime import datetime


class VB(csv.Dialect):
    """Volksbank csv format"""
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


class InvalidInputException(Exception):
    """Exception for input CSVs that seem not to be valid VB input files."""

    def __init__(self, message):
        self.message = message


csv.register_dialect("vb", VB)

vb_field_names = [
    "bezeichnung auftragskonto", "iban auftragskonto", "bic auftragskonto",
    "bankname auftragskonto", "buchungstag", "valutadatum",
    "name zahlungsbeteiligter", "iban zahlungsbeteiligter",
    "bic (swift-code) zahlungsbeteiligter", "buchungstext", "verwendungszweck",
    "betrag", "waehrung", "saldo nach buchung", "bemerkung", "kategorie",
    "steuerrelevant", "glaeubiger id", "mandatsreferenz"
]

homebank_field_names = [
    "date", "paymode", "info", "payee", "memo", "amount", "category", "tags"
]


def _identify_csv_dialect(file_handle, field_names):
    """
    :param file_handle:
    :param field_names:
    :return:
    """
    dialect = csv.Sniffer().sniff(file_handle.readline())
    file_handle.seek(0)
    return csv.DictReader(find_transaction_lines(file_handle),
                          dialect=dialect,
                          fieldnames=field_names)


def convert_vb_cash(file_handle, output_file="homebank.csv"):
    """
    Convert a VB cash file (i.e. normal bank account) to a homebank-readable import CSV.

    :param file_handle: file handle of the file to be converted
    :param output_file: the output file path as a string
    """
    reader = _identify_csv_dialect(file_handle, vb_field_names)
    with open(output_file, 'w', 1, "utf_8") as outfile:
        writer = csv.DictWriter(outfile,
                                dialect='vb',
                                fieldnames=homebank_field_names)
        for row in reader:
            writer.writerow({
                'date': convert_date(row["buchungstag"]),
                'paymode': 8,
                'info': None,
                'payee': row["name zahlungsbeteiligter"],
                'memo': row["verwendungszweck"],
                'amount': row["betrag"],
                'category': None,
                'tags': None
            })


def find_transaction_lines(file):
    """
    Reduce the csv lines to the lines containing actual data relevant for the conversion.

    :param file: The export CSV from VB to be converted
    :return: The lines containing the actual transaction data
    """
    lines = file.readlines()
    i = 1
    for line in lines:
        # simple heuristic to find the csv header line.
        if "Buchungstag" in line and "Betrag" in line:
            return lines[i:]
        i = i + 1


def convert_date(date_string):
    """Convert the date_string to dd-mm-YYYY format."""
    date = datetime.strptime(date_string, "%d.%m.%Y")
    return date.strftime('%d-%m-%Y')


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Convert a CSV export file from VB online banking "
        "to a Homebank compatible CSV format.")
    parser.add_argument("filename", help="The CSV file to convert.")

    parser.add_argument(
        '-o',
        '--output-file',
        help='choose where to store the output file (default: working directory'
    )

    parser.add_argument('--debug',
                        '-d',
                        help='output some information to STDERR')

    return parser.parse_args()


def main():
    args = setup_parser()

    with open(args.filename, 'r', encoding='utf_8') as csv_file:
        output = args.output_file or f"converted_{args.filename.split('/')[-1]}"
        convert_vb_cash(csv_file, output)
        print(f"VB Cash file converted. Output file: {output}"
              ) if args.debug else None


if __name__ == '__main__':
    main()
