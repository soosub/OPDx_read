# OPDx_read

OPDx_read is a small package that reads the proprietary file format OPDx, that is used by Dektak profilometers, and returns numpy arrays

## Installation

Install directly from this fork with pip:

```
pip install git+https://github.com/soosub/OPDx_read.git
```

Or, with [uv](https://docs.astral.sh/uv/), declare it as a git source in your
`pyproject.toml`:

```toml
[tool.uv.sources]
opdx-read = { git = "https://github.com/soosub/OPDx_read.git", branch = "master" }
```

Plotting helpers in `get_data_2D(plot=True)` need `matplotlib` — install
the optional `[plot]` extra to pull it in:

```
pip install "OPDx_read[plot] @ git+https://github.com/soosub/OPDx_read.git"
```

## Basic use

To use it, just open a python console, and type for instance, to extract 1D datas:

```
from OPDx_read.reader import DektakLoad
loader=DektakLoad(filename)
x,y=loader.get_data_1D()
```

or for 2D datas:

```
from OPDx_read.reader import DektakLoad
loader=DektakLoad(filename)
x,y,z=loader.get_data_2D()
```

If you want to extract metadatas, you can call:

```
metadatas=loader.get_metadata()
```

which returns a dictionnary of all the metadatas.