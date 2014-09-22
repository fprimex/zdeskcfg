## zdeskcfg

Python module for easy configuration of zendesk/zdesk scripts.

### Configuration file

The default location for the Python Zendesk configuration used by this module
is `~/.zdeskcfg`. This file can optionally contain the section `zdesk`, and,
under that section, the items:

* email - Zendesk email used for logging in
* password - Zendesk password or API token
* url - Full URL to your Zendesk instance
* token - Indicate if the password field is an API token

    # Example ~/.zdeskcfg
    [zdesk]
    email = you@example.com
    password = 78FLKihfkuh137uijrlkFF88KLIJF
    url = https://example.zendesk.com
    token = 1

### Using zdeskcfg

The idea behind zdeskcfg is to use a common configuration file for all Zendesk
related (Python) scripts. You can expect, by using this module, that the above
described configuration file will be inspected for common Zendesk connection
information. You can then insert your own sections for your own scripts, and
easily leverage both configuration file INI parsing and command line parsing.

All that is required is to define a function, decorate it with
`zdeskcfg.configure`,  and then call it with `zdeskcfg.call`. This looks like
the following:

    import zdeskcfg

    @zdeskcfg.configure(
        my_example_var=('example variable showing zdeskcfg usage',
                  'option', 'x', None, None, 'EXAMPLE_VAR')
        )
    def main(my_example_var='my_example_value'):
        print "my_example_var {}".format(my_example_var)
        for key, val in main.getconfig().iteritems():
            print key, val

    if __name__ == '__main__':
        zdeskcfg.call(main, section='example')

Under the hood, `zdesk.configure` is a class that works as a decorator. It
takes annotations in the style of plac as argument, and wraps the decorated
function (main in this case), which has some operations performed on it. The
main function is granted a new method (remember Python functions are objects)
called `getconfig`. The `getconfig` method returns the values of the zdesk
configuration; either the defaults of `None` and `False`, the values from the
`~/.zdeskcfg` file in the `[zdesk]` section, or the values given on the command
line.

See the [example](https://github.com/fprimex/zdeskcfg/blob/master/example)
script for more detailed comments on the above code.

The result of all of this is that you can share the `[zdesk]` section (and
other sections) of the `~/.zdeskcfg` between all of your scripts. And, since
plac and plac\_ini is being used, the scripts get INI parsing, command line
parsing, and help generation for essentially free.

