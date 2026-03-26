# T9 demo

T9 (Grover et al. 1998) is a
[patented](https://patents.google.com/patent/US5818437A/en) predictive text
entry system originally designed for augmentative and alternative communication
(AAC). However, it was also commonly available on cellular telephones with a 3x4
numeric keypad (i.e., "dumbphones", those without physical or software
alphanumeric keyboards) as an alternative to *multi-tap* (in which, e.g., one
presses "2" three times to get a *c*).

The traditional 3x4 numeric grid is laid out as follows:

    1        2 (abc)  3 (def)
    4 (ghi)  5 (jfk)  6 (mno)
    7 (pqrs) 8 (tuv)  9 (wxyz)
    *        0 (␣)    #

The parentheses give the "alphabet" readings of the numerical keys; "0" is used
for spacebar. Thus one can type, e.g, Thus one can type, e.g, Thus one can type,
e.g, Thus to type either *request* or *pervert* (and various nonwords), for
example, one types e.g, "7378378".

T9 depends in part on a closed lexicon, and a simple language model to
disambiguate between in-lexicon choices. Whlie the original T9 used a word-based
language model, in this demo we'll instead use a character language model. See
Gorman & Sproat 2021:§7.6 for more information.

## The decoder

We first need a transducer mapping from the numerical to alphabetic characters.
The mapping itself is as follows:

```python
t9_map = [("0", [" "]), ("2", ["a", "b", "c"]), ("3", ["d", "e", "f"]),
          ("4", ["g", "h", "i"]), ("5", ["j", "k", "l"]),
          ("6", ["m", "n", "o"]), ("7", ["p", "q", "r", "s"]),
          ("8", ["t", "u", "v"]), ("9", ["w", "x", "y", "z"])]
```

We can turn this into a simple T9 decoder (numeral-to-alphabet) transducer as
follows:

```python
decoder = pynini.Fst()
for inp, outs in t9_map:
    decoder |= pynini.cross(inp, pynini.union(*outs))
decoder.closure().optimize()
```

Alternatively, one could have used `string_map` but this would require entries
in a different format (i.e., pairs of strings).

Next, we build a lexicon acceptor representing the union of all words in the
vocabulary, separated by space:

```python
lexicon = pynini.string_map(lexicon)
# This helper is the FST equivalent of " ".join(...).
lexicon = pynutil.join(lexicon, " ").optimize()
```

Finally, to decode, we use the `decoder` to generate all possible strings, and
the `lexicon` to filter them. Given some `t9_input` string:

```python
# This just does composition and output projection, with some checks.
lattice = rewrite.rewrite_lattice(t9_input, decoder)
# Filters non-lexical paths.
lattice = pynini.intersect(lattice, lexicon)
```

These steps are all provided in a Python class in the Pynini `examples`
submodule,
[`pynini.examples.t9`](https://github.com/kylebgorman/pynini/blob/master/pynini/examples/t9.py):

```python
from pynini.examples import t9

# The argument is an iterable of strings.
my_t9 = t9.T9(lexicon)
lattice = my_t9.decode("737837804726833")
```

Take a quick look at the class to see how it's organized; note for instance that
it has an `encode` method in addition to `decode`.

## Preparing the lexicon

We'll use a bit of English newswire for this. A [simple Bash script](download)
downloads about a year of it:

    ./download

Then, [`char_tokenize.py`](char_tokenize.py) does some simple text normalization
to create alphabetic, whitespace-delimited text. Take a look at this script to
see what it does, then run it like so:

    ./char_tokenize.py > news.txt

The following snippet is then used to build a lexicon out of this data, here
using a Python hash-backed `set`:

```python
def lexicon() -> set[str]:
    result = set()
    with open(SOURCE, "r") as source:
         for line in source:
             result.update(line.split())
    return result
```

We then incorporate this as follows:

```python
my_t9 = t9.T9(lexicon())
```

## Adding a language model

In the example above, `lattice` is an FSA, with multiple paths corresponding to
dozens of distinct alphabetic strings:

    >>> candidates = rewrite.lattice_to_strings(lattice)
    >>> print(f"# of candidates: {len(candidates):,}")
    # of candidates: 4 
    >>> print(candidates)
    ['pervert granted', 'pervert grantee', 'request granted', 'request grantee']

To pick the most likely string, we'll add a simple character language model.
Note that in earlier T9 systems, I believe a word language model was used, but
we'll focus on character modeling instead since you'll be doing that in HW6, and
it's slightly easier in this case.

The [`make_char_lm`](make_char_lm) Bash script builds the language model: as
specified, it is a 6-gram character LM with Witten-Bell smoothing and relative
entropy shrinking. **This takes a few minutes to build**. Run it:

    ./make_char_lm

then take a look at it to see what it does while it's running. It uses UNIX
pipes to avoid the need to name (and later delete) the various temporary files,
though this is sort of hard to get right and it may be easier to just use
temporary files.

To incorporate the LM into decoding, all we need to do is:

- Load the LM (which is just an FST file) into Pynini:

  ```python
  lm = pynini.Fst.read(LM)
  ```

- Compose the lattice with the LM to score the various paths:

  ```python
  lattice @= lm  # This is equivalent to: lattice = lattice @ lm.
  ```

- Compute the highest-probability path (the "shortest path") and convert it to a
  string:

  ```python
  print(f"Best candidate: {rewrite.lattice_to_top_string(lattice)}")
  ```

This prints `request granted`, which is apparently the most likely solution.

## Stretch goals

- Incorporate the character LM system directly into the `T9` class or create a
  derivative class (i.e., a subclass) which uses it internally.
- Modify the system to use a trigram word language model rather than a character
  language model.
  - In place of the lexicon acceptor, compile a lexicon transducer that maps
    from characters to words, ignoring space.
  - Build a word LM and use it to filter.
  - Incorporate the word LM directly into the `T9` class or create a derivative
    class which uses it internally.
- Play with the simple text normalization in `char_tokenize.py` to better fit
  the genre.
- Train a much larger character LM using additional [English news crawl
  data](https://data.statmt.org/news-crawl/en/).
- Experiment with LM hyperparameters, including Markov order, smoothing
  technique, and the amount of shrinkage.

# References.

Gorman, K. and Sproat, R. 2021. *Finite-State Text Processing*. Morgan &
Claypool.

Grover, Dale L., Martin T. King, and Clifford A. Kushler. 1998. Reduced keyboard
disambiguating computer. US Patent 5,818,437.
