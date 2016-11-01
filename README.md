# shmlast

[![Build Status](https://travis-ci.org/camillescott/shmlast.svg?branch=master)](https://travis-ci.org/camillescott/shmlast)
[![codecov](https://codecov.io/gh/camillescott/shmlast/branch/master/graph/badge.svg)](https://codecov.io/gh/camillescott/shmlast)

shmlast is a reimplementation of the [Conditional Reciprocal Best
Hits](https://github.com/cboursnell/crb-blast) algorithm for finding potential orthologs between
a transcriptome and a species-specific protein database. It uses the [LAST](http://last.cbrc.jp/)
aligner and the pydata stack to achieve much better performance while staying in the Python ecosystem. 

## About

As described in the original publication ([Aubry et al.
2014](http://www.plosgenetics.org/article/info%3Adoi%2F10.1371%2Fjournal.pgen.1004365)), conditional
reciprocal best hits (CRBH) builds on the traditional reciprocal best hits (RBH) method for orthology
assignment by training a simple model of the e-value cutoff for a particular length of sequence on
an initial set of RBH's. From their github:

    "Reciprocal best BLAST is a very conservative way to assign orthologs. The main innovation in
    CRB-BLAST is to learn an appropriate e-value cutoff to apply to each pairwise alignment by taking
    into account the overall relatedness of the two datasets being compared. This is done by fitting a
    function to the distribution of alignment e-values over sequence lengths. The function provides the
    e-value cutoff for a sequence of given length."

Unfortunately, the original implementation uses NCBI BLAST+ (which is incredibly slow), and is
implemented in Ruby, which requires users to leave the Python-dominated bioinformatics software
system. shmlast makes this algorithm available to users in Python-land, while also greatly improving
performance by using LAST for initial homology searches. Additionally, shmlast outputs both the raw
parameters and a plot of its model for inspection.

shmlast is designed for finding orthologs between *transcriptomes and protein databases*. As such, it currently does not
support nucleotide-nucleotide or protein-protein alignments. This may be changed in a future version, but for now, 
it remains focused on that task.

Also note that RBH, and by extension CRBH, is meant for comparing between *two species*. Neither of these methods should
be used for annotating a transcriptome with a mixed protein database (like, for example, uniref90).

## Output

shmlast outputs a plain CSV file with the CRBH's, which by default will be named `$QUERY.x.$DATABASE.crbl.csv`. This CSV
file can be easily parsed with Pandas like so:

```Python
import pandas as pd

crbl_df = pd.read_csv('query.x.database.crbl.csv')
```

The columns are:

1. *E*: The e-value.
2. *EG2*: Expected alignments per square giga.
3. *E_scaled*: E-value rescaled for the model (see below for details).
4. *ID*: A unique ID for the alignment.
5. *bitscore*: The bitscore, calculated as (lambda * score - ln[K]) / ln[2].
6. *q_aln_len*: Query alignment length.
7. *q_frame*: Frame in the query translation.
8. *q_len*: Length of the query sequence.
9. *q_name*: Name of the query sequence.
10. *q_start*: Start of query alignment.
11.*q_strand*: Strand of query alignment.
12. *s_aln_len*: Length of subject alignment.
13. *s_len*: Length of subject sequence.
14. *s_name*: Name of subject sequence.
15. *s_start*: Start of subject alignment.
16. *s_strand*: Strand of subject alignment.
17. *score*: The alignment score.

See http://last.cbrc.jp/doc/last-evalues.html for more information on e-values and scores.

#### Model Output

shmlast also outputs its model, both in CSV format and as a plot. The CSV file is named 
`$QUERY.x.$DATABASE.crbl.model.csv`, and has the following columns:

1. *center*: The center of the length bin.
2. *size*: The size of the bin.
3. *left*: The left of the bin.
4. *right*: The right of the bin.
5. *fit*: The scaled e-value cutoff for the bin.

To fit the model, the e-values are first scaled to a more suitable range using the equation
`Es = -log10(E)`, where `Es` is the scaled e-value. e-values of 0 are set to an arbitrarily small
value to allow the log-scaling. The *fit* column of the model is thus this scaled value.

The model plot is named `$QUERY.x.$DATABASE.crbl.model.plot.pdf` by default.

## Installation

I recommend the Anaconda (or miniconda) Python distribution. To install into an Anaconda
environment, first get dependencies via conda:

```bash
conda install --file <(curl https://raw.githubusercontent.com/camillescott/shmlast/master/environment.txt)
```

And then install shmlast and its PyPI dependencies with pip:

```bash
pip install shmlast
```

## Third-party Dependencies

shmlast requires the LAST aligner and gnu-parallel.

### Manually

LAST can be installed manually into your home directory like so:

```bash
cd
curl -LO http://last.cbrc.jp/last-658.zip
unzip last-658.zip
pushd last-658 && make && make install prefix=~ && popd
```

And a recent version of gnu-parallel can be installed like so:

```bash
(wget -O - pi.dk/3 || curl pi.dk/3/ || fetch -o - http://pi.dk/3) | bash
```

### Through a Package Manager

For Ubuntu 16.04 or newer, sufficiently new versions of both are available
through the package manager:

`sudo apt-get install last-align parallel`

For OSX, you can get last through the homebrew-science channel:

```bash
brew tap homebrew/science
brew install last
```

## Library

shmlast is also a Python library. Each component of the pipeline is implemented as a
[pydoit](http://pydoit.org) task and can be used in doit workflows, and the implementations for calculating best hits,
reciprocal best hits, and conditional reciprocal best hits are relatively easily usable as Python
classes. For example, the `lastal` task could be incorporated into a doit file like so:

```Python
from shmlast.last import lastal_task

def task_lastal():
    return lastal_task('query.fna', 'db.faa', translate=True)
```

## Known Issues

There is an incompatibility between seaborn and matplotlib version 1.5.3. For that reason, the
required matplotlib version is locked to 1.5.1.

If you already have matplotlib > 1.5.1 installed (from a virtualenv):

```
pip install https://pypi.python.org/packages/source/m/matplotlib/matplotlib-1.5.1.tar.gz
```

Check that it worked:

```
python
import matplotlib
matplotlib.__version__
quit()
```

## References

1. Aubry S, Kelly S, Kümpers BMC, Smith-Unna RD, Hibberd JM (2014) Deep Evolutionary Comparison of
   Gene Expression Identifies Parallel Recruitment of Trans-Factors in Two Independent Origins of C4
   Photosynthesis. PLoS Genet 10(6): e1004365. doi:10.1371/journal.pgen.1004365

2. O. Tange (2011): GNU Parallel - The Command-Line Power Tool, ;login: The USENIX Magazine,
   February 2011:42-47.

3. Kiełbasa, S. M., Wan, R., Sato, K., Horton, P., & Frith, M. C. (2011). Adaptive seeds tame
   genomic sequence comparison. Genome research, 21(3), 487-493.
