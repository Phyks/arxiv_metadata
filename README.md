Metadata for arXiv
==================

The goal of this repository is to provide a minimal API to put metadata on arXiv papers.

Disclaimer: This code is not scalable nor ready to run in production. In
particular, it might be error-prone, and do not try to be resilient and keep
trace of errors. It is here as a proof of concept and to back [this
article](http://known.phyks.me/2015/lets-some-metadata-on-arxiv) with some
code. However, the `reference_fetcher` part is working quite well, and was able
to extract most of the references from arXiv papers I tested it on. Note that
it is quite long to run it on a paper, mainly due to the latency in [Crossref
API](http://search.crossref.org/).


A demo instance should be available at
[http://arxiv.phyks.me/](http://arxiv.phyks.me/). This may not be very stable
or highly available though.


## Special thanks

Under the hood, this code uses the wonderful [Crossref
API](http://search.crossref.org/) for reference parsing to DOI, which works
really well and with a very large index.

It also uses the [Dissemin API](http://beta.dissem.in/) in the
`reference_fetcher` to try to find Open access versions of referenced papers.

It works using the Open access [arXiv.org](http://arxiv.org) repository,
without which it would be really difficult to achieve similar thing, due to
paywalls and lack of sources. It also uses their
[API](http://arxiv.org/help/api) to fetch DOIs from arXiv id and conversely.


## Introduction

Most of the published scientific papers are availabe online, as preprints. For
physics and computer science, most of them are available on the
[arXiv](http://arxiv.org/) repository. Published paper get a unique (global)
identifier, a [DOI](https://en.wikipedia.org/wiki/Digital_object_identifier).
Preprint papers released on arXiv get a unique
[identifier](https://arxiv.org/help/arxiv_identifier). Correspondance between
these two identifiers can be made quite easily once the preprint is published,
as some publishers pushes back the DOIs to arXiv.

Then, all these articles can be easily identified and tracked. However, very
small use of this is done, and especially there is no way to post metadata
between articles. For example, getting a (usable) list of articles referencing
a given article, or referenced by it, is very difficult (and a textual
bibliography is not a usable list of articles, as it is truly difficult to
parse).

This basic Python code offers a way to add some metadata between articles. One
can import articles in it. It automatically tries to fetch referenced papers
and add the corresponding relationships between these papers and the added
paper. Relationships are reversible which means one can easily get the papers
citing a given paper.

It offers an API to add extra metadata. One could for instance imagine adding
others relations between papers to say they are similar, extra possible
reference, or so on.

One could even imagine extending this further to tag papers, just as arXiv do
(in some sort) with their "categories" (such as
[cond-mat](http://arxiv.org/archive/cond-mat)) so that researchers could follow
tags relative to their area of research, and get a narrower and better targeted
list of papers everyday. Plus everyone could tag articles in a collaborative
way, so that some papers which might be of interest for a field, but were not
tagged as such, would reach it anyway.


## Installation

For building `opendetex` (which is a necessary dependency), you will need
`gcc`, `flex` and `make`.

* Clone this repository: `git clone https://github.com/Phyks/arxiv_metadata`.
* Init submodules (`opendetex`): `git submodule init; git submodule update`.
* Build `opendetex`: `cd reference_fetcher/opendetex; make`.
* [This is all if you only want to use the `reference_fetcher`. Else, go on reading]
* Download required Python modules: `pip install -r requirements.txt`.
* [Optional] Update configuration in `config.py`. Default values are for testing and dev.
* You are ready to go.

## Test it

You can test it easily using the Bottle built-in webserver. This is the default configuration.

To start the app, just run `python3 ./main.py` and head to [http://localhost:8080](http://localhost:8080).


You should not use this server in production, and should edit `main.py` accordingly.

## API

### Index

```
GET /
```

```json
{
    "papers": "/papers/?id={id}&doi={doi}&arxiv_id={arxiv_id}",
}
```

### Get papers

```
GET /papers
Accept: application/vnd.api+json
```

One can filter further using `id={id}`, `doi={doi}` or `arxiv_id={arxiv_id}`
query parameters.

```json
    {
        "data": [
            {
                "type": "papers",
                "id": 1,
                "attributes": {
                    "doi": "10.1126/science.1252319",
                    "arxiv_id": "1401.2910"
                },
                "links": {
                    "self": "/papers/1"
                },
                "relationships": {
                    "cite": {
                        "links": {
                            "related": "/papers/1/relationships/cite"
                        }
                    },
                    ...
                }
            }
        ]
    }
```


### Get a paper

```
GET /papers/1
Accept: application/vnd.api+json
```

```json
{
    "data": {
        "type": "papers",
        "id": 1,
        "attributes": {
            "doi": "10.1126/science.1252319",
            "arxiv_id": "1401.2910"
        },
        "links": {
            "self": "/papers/1"
        },
        "relationships": {
            "cite": {
                "links": {
                    "related": "/papers/1/relationships/cite"
                }
            },
            ...
        }
    }
}
```


### Get the relationships of a paper

```
GET /papers/1/relationships/cite
Accept: application/vnd.api+json
```

```json
{
    "links": {
        "self": "/papers/1/relationships/cite",
        "related": "/papers/1/cite"
    },
    "data": [
        {
            "type": "papers",
            "id": 2,
        },
        ...
    ]
}
```

The previous relationship is to be understood as `paper 1 cites paper 2`.

Using `?reverse=1`, one can reverse the relationships (ie get results for
papers that cites the paper identified by the id in the URL, in the previous
case).


### Post a paper

```
POST /papers
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": {
        "doi": "10.1126/science.1252319",
        // OR
        "arxiv_id": "1401.2910"
    }
}
```

`arxiv_id` (respectively `doi`) is fetched automatically if available.

```json
{
    "data": {
        "type": "papers",
        "id": 1,
        "attributes": {
            "doi": "10.1126/science.1252319",
            "arxiv_id": "1401.2910"
        },
        "links": {
            "self": "/papers/1"
        },
        "relationships": {
            "cite": {
                "links": {
                    "related": "/papers/1/relationships/cite"
                }
            },
            ...
        }
    }
}
```


### Get tags

```
GET /tags
Accept: application/vnd.api+json
```

Filtering is possible using ``id=ID``, ``name=NAME`` or any combination of
these GET parameters. Other parameters are ignored.

```json
{
    "data": [
        {
            "type": "tags",
            "id": 1,
            "attributes": {
                "name": "foobar",
            },
            "links": {
                "self": "/tags/1"
            }
        }
    ]
}
```


### Get a tag by id

```
GET /tag/1
Accept: application/vnd.api+json
```

```json
{
    "data": {
        "type": "papers",
        "id": 1,
        "attributes": {
            "doi": "10.1126/science.1252319",
            "arxiv_id": "1401.2910"
        },
        "links": {
            "self": "/papers/1"
        },
        "relationships": {
            "cite": {
                "links": {
                    "related": "/papers/1/relationships/cite"
                }
            },
            …
        }
    }
}
```

### Create a tag

```
POST /tags
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": {
        "name": "foobar",
    }
}
```

```json
{
    "data": {
        "type": "tags",
        "id": 1,
        "attributes": {
            "name": "foobar",
        },
        "links": {
            "self": "/tags/1"
        }
    }
}
```


### Create a relationship between two papers

```
POST /papers/1/relationships/cite
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": [
        { "type": "cite", "id": "2" },
        ...
    ]
}
```

Response is empty HTTP 204.


### Add a tag to a paper

```
POST /papers/1/relationships/tags
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": [
        { "type": "tags", "id": "2" },
        ...
    ]
}
```

`id` is the id of the tag, which has to be created previously.

Response is empty HTTP 204.


### Delete a paper and associated relationships

```
DELETE /papers/1
Accept: application/vnd.api+json
```

Response is empty HTTP 204.


### Delete a tag

```
DELETE /tags/1
Accept: application/vnd.api+json
```

Response is empty HTTP 204.


### Delete a relationship between two papers

```
DELETE /papers/1/relationships/cite
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": [
        { "type": "cite", "id": "2" },
        ...
    ]
}
```

Response is empty HTTP 204.


### Deleting a tag for a paper

```
DELETE /papers/1/relationships/tags
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
    "data": [
        { "type": "tags", "id": "2" },
        ...
    ]
}
```

`id` is the id of the tag.

Response is empty HTTP 204.


## Associated library

`reference_fetcher` is a module you can use to:

* Fetch DOIs (or arXiv ids) of papers referenced by a given paper on arXiv (or any other paper, provided that you have a .bbl file).
* Fetch DOI associated with a given arXiv paper (if any).
* Fetch the arXiv identifier associated to a given DOI (if any).
* and more :)

`fetch_references.py` script in the root folder is here to show you how to use it and to serve as a minimal example.

### Usage

* `./fetch_references.py some_file.bbl` to get a list of DOIs associated to each `\bibitem`.
* `./fetch_references.py arxiv_eprint_id` to get a list of DOIs associated to each reference from the provided arXiv eprint.


### Example

```
$ ./fetch_references.py 1401.2910
```

```
{'author Barahona, F. title On the computational complexity of I sing spin glass models . journal Journal of Physics A: Mathematical and General volume 15 , pages 3241 ( year 1982 )': 'http://dx.doi.org/10.1088/0305-4470/15/10/028',
 'author Bennett, C. , author Bernstein, E. , author Brassard, G. author Vazirani, U. title Strengths and weaknesses of quantum computing . journal SIAM Journal on Computing volume 26 , pages 1510-1523 ( year 1997 )': 'http://dx.doi.org/10.1137/s0097539796300933',
 'author Berkley, A. J. et al. title A scalable readout system for a superconducting adiabatic quantum optimization system . journal Superconductor Science and Technology volume 23 , pages 105014 ( year 2010 )': 'http://dx.doi.org/10.1088/0953-2048/23/10/105014',
 'author Berry, D. W. , author Childs, A. M. , author Cleve, R. , author Kothari, R. author Somma, R. D. title Exponential improvement in precision for simulating sparse hamiltonians . journal arXiv:1312.1414 ( year 2013 )': 'http://arxiv.org/abs/1312.1414',
 'author Boixo, S. , author Albash, T. , author Spedalieri, F. M. , author Chancellor, N. author Lidar, D. A. title Experimental signature of programmable quantum annealing ( year 2012 ). . 1212.1739': 'http://arxiv.org/abs/1212.1739',
 'author Boixo, S. et al. title Quantum annealing with more than one hundred qubits ( year 2013 ). . 1304.4595': 'http://arxiv.org/abs/1304.4595',
 'author Dechter, R. title Bucket elimination: A unifying framework for reasoning . journal Artificial Intelligence volume 113 , pages 41-85 ( year 1999 )': 'http://dx.doi.org/10.1016/s0004-3702(99)00059-4',
 'author Farhi, E. et al. title A quantum adiabatic evolution algorithm applied to random instances of an NP -complete problem . journal Science volume 292 , pages 472-475 ( year 2001 )': 'http://dx.doi.org/10.1126/science.1057726',
 'author Feynman, R. title Simulating physics with computers . journal International Journal of Theoretical Physics volume 21 , pages 467-488 ( year 1982 )': 'http://dx.doi.org/10.1007/bf02650179',
 'author Grover, L. K. title Quantum mechanics helps in searching for a needle in a haystack . journal Physical Review Letters volume 79 , pages 325-328 ( year 1997 )': 'http://dx.doi.org/10.1103/physrevlett.79.325',
 'author Harris, R. et al. title Experimental investigation of an eight-qubit unit cell in a superconducting optimization processor . journal Phys. Rev. B volume 82 , pages 024511 ( year 2010 )': 'http://dx.doi.org/10.1103/physrevb.82.024511',
 'author Helmut G. Katzgraber, R. S. A., Firas Hamze . title Glassy Chimeras are blind to quantum speedup: Designing better benchmarks for quantum annealing machines ( year 2014 ). . 1401.1546': 'http://arxiv.org/abs/1401.1546',
 'author Isakov, S. , author Zintchenko, I. , author Ronnow, T. author Troyer, M. title Optimized simulated annealing for Ising spin glasses ( year 2014 ). . 1401.1084': 'http://arxiv.org/abs/1401.1084',
 'author Johnson, M. W. et al. title A scalable control system for a superconducting adiabatic quantum optimization processor . journal Superconductor Science and Technology volume 23 , pages 065004 ( year 2010 )': 'http://dx.doi.org/10.1088/0953-2048/23/6/065004',
 'author Johnson, M. W. et al. title Quantum annealing with manufactured spins . journal Nature volume 473 , pages 194-198 ( year 2011 )': None,
 'author Kadowaki, T. author Nishimori, H. title Quantum annealing in the transverse I sing model . journal Phys. Rev. E volume 58 , pages 5355-5363 ( year 1998 )': 'http://dx.doi.org/10.1103/physreve.58.5355',
 'author Kirkpatrick, S. , author Gelatt, C. D. author Vecchi, M. P. title Optimization by simulated annealing . journal Science volume 220 , pages 671-680 ( year 1983 )': 'http://dx.doi.org/10.1126/science.220.4598.671',
 'author Lloyd, S. title Universal quantum simulators . journal Science volume 273 , pages 1073-1078 ( year 1996 )': 'http://dx.doi.org/10.1126/science.273.5278.1073',
 'author Marto n n ak, R. , author Santoro, G. E. author Tosatti, E. title Quantum annealing by the path-integral M onte C arlo method: The two-dimensional random I sing model . journal Phys. Rev. B volume 66 , pages 094203 ( year 2002 )': 'http://dx.doi.org/10.1103/physrevb.66.094203',
 'author McGeoch, C. C. author Wang, C. title Experimental evaluation of an adiabatic quantum system for combinatorial optimization . In booktitle Proceedings of the 2013 ACM Conference on Computing Frontiers ( year 2013 )': 'http://dx.doi.org/10.1145/2482767.2482797',
 'author Papageorgiou, A. author Traub, J. F. title Measures of quantum computing speedup . journal Phys. Rev. A volume 88 , pages 022316 ( year 2013 )': 'http://dx.doi.org/10.1103/physreva.88.022316',
 'author Parberry, I. title Parallel speedup of sequential machines: a defense of parallel computation thesis . journal SIGACT News volume 18 , pages 54-67 ( year 1986 )': 'http://dx.doi.org/10.1145/8312.8317',
 'author Pomerance, C. title A tale of two sieves . journal Notices of the Amer. Math. Soc. volume 43 , pages 1473-1485 ( year 1996 )': None,
 'author Pudenz, K. L. , author Albash, T. author Lidar, D. A. title Error corrected quantum annealing with hundreds of qubits . journal arXiv:1307.8190 ( year 2013 )': 'http://arxiv.org/abs/1307.8190',
 'author Santoro, G. E. , author Marto n a k, R. , author Tosatti, E. author Car, R. title Theory of quantum annealing of an I sing spin glass . journal Science volume 295 , pages 2427-2430 ( year 2002 )': None,
 'author Santra, S. , author Quiroz, G. , author Steeg, G. V. author Lidar, D. title MAX 2-SAT with up to 108 qubits . journal arXiv:1307.3931 ( year 2013 )': 'http://arxiv.org/abs/1307.3931',
 'author Sarandy, M. S. author Lidar, D. A. title Adiabatic quantum computation in open systems . journal Physical Review Letters volume 95 , pages 250503- ( year 2005 )': 'http://dx.doi.org/10.1103/physrevlett.95.250503',
 'author Shor, P. W. title Algorithms for quantum computation: discrete logarithms and factoring . journal Foundations of Computer Science, 1994 Proceedings., 35th Annual Symposium on pages 124-134 ( year 20-22 Nov 1994 )': 'http://dx.doi.org/10.1109/sfcs.1994.365700',
 'author Smolin, J. A. , author Smith, G. author Vargo, A. title Oversimplifying quantum factoring . journal Nature volume 499 , pages 163-165 ( year 2013 )': 'http://dx.doi.org/10.1038/nature12290',
 'author Smolin, J. A. author Smith, G. title Classical signature of quantum annealing ( year 2013 ). . arXiv:1305.4904': 'http://arxiv.org/abs/1305.4904',
 'author Somma, R. D. , author Nagaj, D. author Kieferov a , M. title Quantum speedup by quantum annealing . journal Physical Review Letters volume 109 , pages 050501- ( year 2012 )': 'http://dx.doi.org/10.1103/physrevlett.109.050501',
 "author Wang, L. et al. title Comment on: 'Classical signature of quantum annealing ' ( year 2013 ). . arXiv:1305.5837": 'http://arxiv.org/abs/1305.5837',
 'author Young, A. P. author Katzgraber, H. G. title Absence of an Almeida-Thouless Line in Three-Dimensional Spin Glasses . journal Phys. Rev. Lett. volume 93 , pages 207203 ( year 2004 )': 'http://dx.doi.org/10.1103/physrevlett.93.207203',
 'note For example, it may be the case, though it seems unlikely, that a classified polynomial-time factoring algorithm is available to parts of the intelligence community': None,
 'note Such a proof seems unlikely to be found any time soon since it would imply that factoring is not in the complexity class P (polynomial) and thus P and NP (nondeterministic polynomial) are distinct, solving the long-standing P versus NP question': None,
 "note We compare quantum annealing only to classical simulated annealing and simulated quantum annealing in this study. Another example of a limited quantum speedup would be Shor's factoring algorithm running on a fully coherent quantum computer vs a classical computer where the period finding using a quantum circuit has been replaced by a classical period finding algorithm": None,
 'note While one can in principle look for an optimal annealing time for each individual problem instance, we instead determine an averaged optimal annealing time for each problem size by annealing many instances at various annealing times , and then use these for all future problems of that size': None}
```

---


```
$ ./fetch_reference.py /tmp/test.bbl
```

```
{'Abrikosov A. A., Gorʹkov L. P., Dzyaloshinski I. E. Dzi͡aloshinskiĭ I. E. Methods Of Quantum Field Theory In Statistical Physics (Dover Publications) 1975': None,
 'Arnold P. Moore G. Phys. Rev. Lett. 87 2001 120401': None,
 'Baym G., Blaizot J.-P., Holzmann M., Lalo e F. Vautherin D. Phys. Rev. Lett. 83 1999 1703': 'http://dx.doi.org/10.1103/physrevlett.83.1703',
 "Capogrosso-Sansone B., Giorgini S., Pilati S., Pollet L., Prokof'ev N., Svistunov B. Troyer M. New Journal of Physics 12 2010 043010": 'http://dx.doi.org/10.1088/1367-2630/12/4/043010',
 'Donnelly R. J. Phys. Today 62 2009 34–39': 'http://dx.doi.org/10.1063/1.3248499',
 'Griffin A. Zaremba E. Phys. Rev. A 56 1997 4839': 'http://dx.doi.org/10.1103/physreva.56.4839',
 'Hou Y.-H., Pitaevskii L. P. Stringari S. Phys. Rev. A 88 2013 043630': 'http://dx.doi.org/10.1103/physreva.88.043630',
 'Hu H., Taylor E., Liu X.-J., Stringari S. Griffin A. New Journal of Physics 12 2010 043040': 'http://dx.doi.org/10.1088/1367-2630/12/4/043040',
 "Kashurnikov V. A., Prokof'ev N. V. Svistunov B. V. Phys. Rev. Lett. 87 2001 120402": 'http://dx.doi.org/10.1103/physrevlett.87.120402',
 'Ku M. J. H., Sommer A. T., Cheuk L. W. Zwierlein M. W. Science 335 2012 563': 'http://dx.doi.org/10.1126/science.1214987',
 'Landau L. D. J. Phys. USSR 11 1947 91': None,
 'Landau L. D. Lifshitz E. M. Fluid Mechanics, Second Edition: Volume 6 (Course of Theoretical Physics) 2nd Edition Course of theoretical physics / by L. D. Landau and E. M. Lifshitz, Vol. 6 (Butterworth-Heinemann) 1987': 'http://dx.doi.org/10.1016/b978-0-08-050347-9.50001-0',
 'Lee T. D. Yang C. N. Phys. Rev. 113 1959 1406': 'http://dx.doi.org/10.1103/physrev.113.1406',
 'Meppelink R., Koller S. B. van der Straten P. Phys. Rev. A 80 2009 043605': 'http://dx.doi.org/10.1103/physreva.80.043605',
 'Ozawa T. Stringari S. Phys. Rev. Lett. 112 2014 025302': 'http://dx.doi.org/10.1103/physrevlett.112.025302',
 'Peshkov V. P. J. Phys. USSR 8 1944 381': None,
 'Pitaevskii L. P. Stringari S. Bose-Einstein condensation (Clarendon Press, Oxford New York) 2003': 'http://dx.doi.org/10.1023/b:joss.0000028243.07395.b3',
 'Sidorenkov L. A., Tey M. K., Grimm R., Hou Y.-H., Pitaevskii L. Stringari S. Nature 498 2013 78 letter': 'http://dx.doi.org/10.1038/nature12136',
 'Taylor E., Hu H., Liu X.-J., Pitaevskii L. P., Griffin A. Stringari S. Phys. Rev. A 80 2009 053601': 'http://dx.doi.org/10.1103/physreva.80.053601'}
 ```
