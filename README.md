Metadata for arXiv
==================

## Installation

For building `opendetex` (which is a necessary dependency), you will need
`gcc`, `flex` and `make`.

* Clone this repository: `git clone https://github.com/Phyks/arxiv_metadata`.
* Init submodules (`opendetex`): `git submodule init; git submodule update`.
* Build `opendetex`: `cd opendetex; make`.
* You are ready to go.

## Usage

`./main.py some_file.bbl` to get a list of DOIs associated to each `\bibitem`.
