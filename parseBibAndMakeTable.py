import logging
import requests
import bibtexparser
import argparse

def main():

    parser = argparse.ArgumentParser(description='Parses an ORCID bibtex export, and prints a nice flat text file with Altmetric and citations added.')
    parser.add_argument('-file', help='Alternative filename for the ORCID export. Default: "works.bib".', default='works.bib')
    parser.add_argument('-logname', help='Where the logs should be sorted. Default: "arc_friend.log"', default='arc_friend.log')

    args = parser.parse_args()

    logging.basicConfig(filename=args.logname, level=logging.INFO, filemode='w')

    with open(args.file) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    '''
    I want the final output to look like this:
        10. Person, A., Person, B., Person, C., Another Person, C., 2011. Cautionary notes on the use of APIs. API journal 23, 3871–8.
        Impact Factor = 10.11
        Citations = 12
        AltMetric score = 0
    '''

    for counter, e in enumerate(bib_database.entries, start=1):
        author_string = e['author']
        author_list = author_string.replace('{','').replace('}','').split('and')
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
                newa += a.split()[0] + ' '
                newa += '.'.join([substring[0] for substring in a.split()[1:]])
            else:
                # last name is last
                newa += a.split()[-1] + ', '
                newa += '.'.join([substring[0] for substring in a.split()[:-1]])
            # add missing dot at end of first name
            if newa[-1] != '.':
                newa += '.'
            shortened_author_list.append(newa)

        shortened_author_string = ', '.join(shortened_author_list)

        journal = e['journal']
        doi = e['doi']
        title = e['title']
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


        if not year:
            overall_string = f'{counter}. {shortened_author_string}, {year}. {title}. {journal}, {volume}, {pages}.'
        if volume and pages:
            overall_string = f'{counter}. {shortened_author_string}, {year}. {title}. {journal}, {volume}, {pages}.'
        if not volume and pages:
            overall_string = f'{counter}. {shortened_author_string}, {year}. {title}. {journal}, {pages}.'
        if not volume and not pages:
            overall_string = f'{counter}. {shortened_author_string}, {year}. {title}. {journal}.'
        if not year:
            overall_string = f'{counter}. {shortened_author_string}. {title}. {journal}, {volume}, {pages}.'

        # now get the citations

        # http://api.crossref.org/works/10.1179/1942787514y.0000000039 for example
        crossref_url = f'http://api.crossref.org/works/{doi}'

        r = requests.get(crossref_url)
        reference_count = r.json()['message']['reference-count']
        
        # 'https://api.altmetric.com/v1/doi/10.1038/news.2011.490'
        altmetric_url = f'https://api.altmetric.com/v1/doi/{doi}'
        r = requests.get(altmetric_url)
        altmetric_score = r.json()['score']

        overall_string += f'\nImpact Factor = FILLME\nCitations = {reference_count}\nAltmetric score = {altmetric_score}'
        print(overall_string)

if __name__ == '__main__':
    main()
