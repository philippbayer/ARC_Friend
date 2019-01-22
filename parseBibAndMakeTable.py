import logging
import requests
import bibtexparser
from bibtexparser.bparser import BibTexParser
import argparse

def main():

    parser = argparse.ArgumentParser(description='Parses an ORCID bibtex export, and prints a nice flat text file with Altmetric and citations added.')
    parser.add_argument('-file', help='Alternative filename for the ORCID export. Default: "works.bib".', default='works.bib')
    parser.add_argument('-logname', help='Where the logs should be sorted. Default: "arc_friend.log"', default='arc_friend.log')

    args = parser.parse_args()

    logging.basicConfig(filename=args.logname, level=logging.INFO, filemode='w')

    parser = BibTexParser(common_strings=False) #The common_strings option needs to be set when the parser object is created and has no effect if changed afterwards.
    parser.ignore_nonstandard_types = False
    parser.homogenise_fields = True

    with open(args.file) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser)

    '''
    I want the final output to look like this:
        10. Person, A., Person, B., Person, C., Another Person, C., 2011. Cautionary notes on the use of APIs. API journal 23, 3871–8.
        Impact Factor = 10.11
        Citations = 12
        AltMetric score = 0
    '''


    for counter, e in enumerate(bib_database.entries, start=1):
        e = bibtexparser.customization.homogenize_latex_encoding(e)
        # get rid of names like "Marie Kubal\\'akov\\'a"
        e = bibtexparser.customization.convert_to_unicode(e)
        author_string = e['author']
        author_list = author_string.replace('{','').replace('}','').split(' and ')
        # shorten the first names
        # Farquard Banana becomes F.B.
        shortened_author_list = []
        # two possible names for some reason returned by ORCID
        # Bayer, {Philipp E.} so the last name is first
        # Candy M. Taylor so the last name is last
        for a in author_list:
            a = a.strip()
            newa = ''
            if not a: continue
            if ',' in a:
                # last name is first:
                # last name
                newa += a.split()[0] + ' '
                # first name
                newa += '.'.join([substring[0] for substring in a.split()[1:]])
            elif a.split()[-1].isupper():
                # Bayer PE
                newa += a.replace(' ',', ')
            else:
                # last name is last
                newa += a.split()[-1] + ', '
                newa += '.'.join([substring[0] for substring in a.split()[:-1]])
            # add missing dot at end of first name
            if newa[-1] != '.':
                newa += '.'
            shortened_author_list.append(newa)

        shortened_author_string = ', '.join(shortened_author_list)

        if 'booktitle' in e:
            journal = e['booktitle']
        else:
            try:
                journal = e['journal'].replace('\\','').replace('}','').replace('{','')
            except KeyError:
                journal = False

        try:
            doi = e['doi']
        except KeyError:
            logging.info(f'{title} has no doi, skipping (for now?)')
            continue

        title = e['title'].replace('}','').replace('{','').replace('\n','').replace('\r','')
        if journal == 'Zenodo' or 'ZENODO' in doi:
            logging.info(f'Skipping cited dataset {title}, {doi} at Zenodo (for now?)')
            continue
        try:
            year = e['year']
        except KeyError:
            year = False

        try:
            volume = e['volume']
        except KeyError:
            volume = False
        try:
            pages = e['pages']
        except KeyError:
            pages = False

        overall_string = f'{counter}. {shortened_author_string}, {year}. {title}.'
        if journal:
            overall_string += f' {journal}, '
        if volume:
            overall_string += f' {volume}, '
        if pages:
            overall_string += f' {pages}.'

        overall_string = overall_string.strip()
        overall_string = overall_string.replace('  ',' ')
        if overall_string[-1] == ',':
            overall_string = overall_string.rstrip(',') + '.'

        # now get the citations
        # http://api.crossref.org/works/10.1179/1942787514y.0000000039 for example
        crossref_url = f'http://api.crossref.org/works/{doi}'

        r = requests.get(crossref_url)
        reference_count = r.json()['message']['is-referenced-by-count']
        
        # 'https://api.altmetric.com/v1/doi/10.1038/news.2011.490'
        altmetric_url = f'https://api.altmetric.com/v1/doi/{doi}'
        r = requests.get(altmetric_url)
        altmetric_score = r.json()['score']

        overall_string += f'\nImpact Factor = FILLME\nCitations = {reference_count}\nAltmetric score = {altmetric_score}\n'
        overall_string = overall_string.replace('..','')
        print(overall_string)

if __name__ == '__main__':
    main()
