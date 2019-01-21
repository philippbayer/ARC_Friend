

# ARC Friend

For my ARC DECRA application I wanted a list of citations, including citations, journal impact factor, and AltMetrics score.

This script parses the file generated by the ORCID export function, then uses public APIs to get Altmetric, journal impact factor (TODO), and citations. Unfortunately there is no public journal impact factor API, so the user will have to fill that in manually (for now?).

This does NOT currently work nicely, but I'm getting there!

## Dependencies

Only bibtexparser (`pip3 install bibtexparser`). I have not tested this script under Python 2.x.

## Usage:

First, export your ORCID profile using the button at https://orcid.org/my-orcid:

![ORCID button](button.png)

Then, move the exported works.bib into the current directory and run this:

    python parseBibAndMakeTable.py

That will print the final table to standard out.

Alternatively, you can specify the path:

    python parseBibAndMakeTable.py --file /home/potato/Downloads/otherworks.bib

assumes that you renamed your ORCID export to otherworks.bib.


Example *buggy* output:

```
1. Mousavi-Derazmahalleh, M., Bayer, P.E., Hane, J.K., Babu, V., Nguyen, H.T., Nelson, M.N., Erskine, W., Varshney, R.K., Papa, R., Edwards, D., 2019. Adapting legume crops to climate change using genomic approaches. Plant, Cell and Environment., 42, 6--19.
Impact Factor = FILLME
Citations = 3
Altmetric score = 9.556

2. C, ., Taylor, y.M., Kamphuis, L.G., Zhang, W., Garg, G., Berger, J.D., Mousavi-Derazmahalleh, M., Bayer, P.E., Edwards, D., Singh, K.B., Cowling, W.A., Nelson, M.N., 2018. INDEL variation in the regulatory region of the major flowering time gene LanFTc1is associated with vernalization response and flowering time in narrow-leafed lupin (Lupinus angustifolius L.). Plant, Cell & Environment.
Impact Factor = FILLME
Citations = 4
Altmetric score = 0.25

3. Mousavi-Derazmahalleh, M., Nevado, B., Bayer, P.E., Filatov, D.A., Hane, J.K., Edwards, D., Erskine, W., Nelson, M.N., 2018. The western Mediterranean region provided the founder population of domesticated narrow-leafed lupin. TAG. Theoretical and applied genetics. Theoretische und angewandte Genetik, 131, 2543--2554.
Impact Factor = FILLME
Citations = 0
Altmetric score = 2.35

```


