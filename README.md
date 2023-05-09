## zdeskcfg

Python module for easy configuration of zendesk/zdesk scripts.

### Configuration file

The default location for the Python Zendesk configuration used by this module
is `~/.zdeskcfg`. This file can contain the section `[zdesk]`, and underneath
that, the items:

* `email` - Email address used for logging in
* `password` - Zendesk password or API token
* `oauth` - Zendesk OAuth token
* `url` - Full URL to your Zendesk instance
* `token` - Indicate if the password field is an API token

Example contents of `~/.zdeskcfg`, separated by method of authentication:

* [Basic Authentication](https://developer.zendesk.com/rest_api/docs/support/introduction#basic-authentication)
```
[zdesk]
url = https://zdesk.zendesk.com
email = you@example.com
password = Z€Nd3$k
token = 0
```

* [API token](https://developer.zendesk.com/rest_api/docs/support/introduction#api-token)
```
[zdesk]
url = https://zdesk.zendesk.com
email = you@example.com
password = f4Pe8DBBK4K674Au7ffcp1j5t2mG7z4e1wvQE6CZ
token = 1
```

**Note**: the `token` field must be set to `1` for **API** authentication.

* [OAuth access token](https://developer.zendesk.com/rest_api/docs/support/introduction#oauth-access-token)
```
[zdesk]
url = https://zdesk.zendesk.com
oauth = 7c6cbb4eac23cd03cf5d9b67ad23993cfb55e2f9049799adac9ada2e69567959
```

**Note**: the `email` field may be omitted because the token acts as a
username & passphrase combination.

Add production and sandbox credentials under separate sections, call via the
name of each `[section]` (e.g. `zdeskcfg.get_ini_config(section='sandbox')`)
```
[zdesk]
url = https://zdesk.zendesk.com
oauth = d768ab1e418e2f2498e2c862843591972697603efb1cc806d2be62de60e857cd

[sandbox]
url = https://zdesk1865746743.zendesk.com
email = you@example.com
password = QCR6dWzbQ9z85D3kh6GWBHBNe6LbZk4n36eZ5x88
token = 1
```

### Using zdeskcfg

The idea behind zdeskcfg is to use a common configuration file for all Zendesk
related (Python) scripts. You can expect, by using this module, that the above
described configuration file will be inspected for common Zendesk connection
information. You can then insert your own sections for your own scripts, and
easily leverage both configuration file INI parsing and command line parsing.

All that is required is to define a function, decorate it with
`zdeskcfg.configure`,  and then call it with `zdeskcfg.call`. This looks like
the following:

    from __future__ import print_function

    import zdeskcfg

    @zdeskcfg.configure(
        ex_var=('example variable showing zdeskcfg usage',
                  'option', 'x', None, None, 'EX')
        )
    def main(ex_var='ex_val'):
        "The function docstring is used as help message usage description."
        print("ex_var", ex_var)
        zdesk_config = main.getconfig()
        for key in zdesk_config.keys():
            print(key, zdesk_config[key])

    if __name__ == '__main__':
        zdeskcfg.call(main, section='example')

Example help output:

    usage: example [-h] [-x EX] [--zdesk-email EMAIL] [--zdesk-password PW]
                   [--zdesk-url URL] [--zdesk-token]

    The function docstring is used as help message usage description.

    optional arguments:
      -h, --help           show this help message and exit
      -x EX, --ex-var EX   example variable showing zdeskcfg usage
      --zdesk-email EMAIL  zendesk login email
      --zdesk-password PW  zendesk password or token
      --zdesk-url URL      zendesk instance URL
      --zdesk-token        specify if password is a zendesk token

Example runs:

    $./example
    ex_var ex_val
    zdesk_email you@example.com
    zdesk_url https://example.zendesk.com
    zdesk_password OIJjjlakjdifjoijf766
    zdesk_token True

    $./example -x EXAMPLE
    ex_var EXAMPLE
    zdesk_email you@example.com
    zdesk_url https://example.zendesk.com
    zdesk_password OIJjjlakjdifjoijf766
    zdesk_token True

    $./example -x EXAMPLE --zdesk-url https://examplesandbox.zendesk.com
    ex_var EXAMPLE
    zdesk_email you@example.com
    zdesk_url https://examplesandbox.zendesk.com
    zdesk_password OIJjjlakjdifjoijf766
    zdesk_token True


Under the hood `zdesk.configure` is a class that works as a decorator. It takes
annotations in the style of [plac](https://code.google.com/p/plac/) and
[plac\_ini](https://github.com/fprimex/plac_ini) as argument, and wraps the
decorated function (main in this case), which has some operations performed on
it. The main function is granted a new method (remember Python functions are
objects) called `getconfig`. The `getconfig` method returns the values of the
zdesk configuration; either the defaults of `None` and `False`, the values from
the `~/.zdeskcfg` file in the `[zdesk]` section, or the values given on the
command line. `getconfig` can also return the `email`, etc, items under any
specified section of the ini file. Any missing items will be supplied by the
`[zdesk]` section or the defaults, and any command line options will still
override.

See the [example](https://github.com/fprimex/zdeskcfg/blob/master/example)
script for more detailed comments on the above code.

The result of all of this is that you can share the `[zdesk]` section (and
other sections) of the `~/.zdeskcfg` between all of your scripts. And, since
plac and plac\_ini are being used, the scripts get INI parsing, command line
parsing, and help generation for essentially free.

There is also a module-level convenience function, `get_ini_config`, that works
like the `getconfig` method. You can directly get at the ini file configuration
without needing to declare and decorate your own function. For example:

    >>> import zdeskcfg
    >>> zdeskcfg.get_ini_config()
    >>> zdeskcfg.get_ini_config(section='sandbox')

This is done by just internally decorating an empty placeholder function, then
using it to retrieve the configuration. This has all of the same behavior as
`getconfig`, except obviously there are no command line arguments.

The output of `getconfig` and `zdeskcfg.get_ini_config` is made to go directly
into the zdesk.Zendesk constructor.

    >>> import zdeskcfg
    >>> from zdesk import Zendesk
    >>> zd = Zendesk(**zdeskcfg.get_ini_config())

