# pyeti

A Python package of awesome stuff.

## Install

`pip install pyeti` or `pip install -e 'git+https://github.com/cehdeti/pyeti.git@master#egg=pyeti'`

## Usage

### CLI

```
from pyeti.cli import confirm

result = confirm('Do you really want to hurt me? [y/N]', default=False)
```

### Utils

```
from pyeti.utils import empty_context as no_transaction

with transaction.atomic() if transact else no_transaction():
    ...

from pyeti.utils import ignore_exception

@ignore_exception(KeyError)
def get_my_key():
    return hello['my_key']
```

### Jokes

The cap_second utility will always capitalize the second letter in a python string.

```
from pyeti.jokes import cap_second

string_to_cap_second='Tsthoeu stnahooOTO tnhoustnh'

cap_second(string_to_cap_second)
> 'tSthoeu Stnahoooto Tnhoustnh'

cap_second(string_to_cap_second)
> 'TSthoeu stnahoooto tnhoustnh'
```

## Contributing

Install dependencies with `pip install -r requirements.txt`. Check your code style with `pep8 .`.
