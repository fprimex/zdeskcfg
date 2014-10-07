import sys
import os
import inspect
import plac
import plac_ini


# Based on a decorator that modified the call signature for a function
# http://www.pythoneye.com/184_18642398/
# http://stackoverflow.com/questions/18625510/how-can-i-programmatically-change-the-argspec-of-a-function-not-in-a-python-de
class configure(object):
    """
    zdeskcfg.configure is a decorator that will add to the given object
    a call signature that includes the standard Zendesk configuration items.
    This effectively converts the given, decorated function, tgt_func, into
    a callable object. It then also provides a getconfig method that the
    decorated function can use to retrieve the Zendesk specific configuration
    items.

    The arguments to zdeskcfg.configure should be plac-style annotations for
    the function being decorated.

    As a result of employing the decorator and using zdeskcfg.call, the
    decorated function will first apply function defaults, then override
    those defaults with the contents of ~/.zdeskcfg, then override that
    using options specified on the command line. This is all done with
    plac_ini and plac.

    See the example script in the zdeskcfg source distribution.
    """
    def __init__(self, **ann):
        self.ann = ann
        self.wrapped = None
        self.__config = {}

    def __call__(self, tgt_func):
        tgt_argspec = inspect.getargspec(tgt_func)
        need_self = False
        if tgt_argspec[0][0] == 'self':
            need_self = True

        name = tgt_func.__name__
        argspec = inspect.getargspec(tgt_func)
        if argspec[0][0] == 'self':
            need_self = False
        if need_self:
            newargspec = (['self'] + argspec[0],) + argspec[1:]
        else:
            newargspec = argspec

        # This gets the original function argument names for actually
        # calling the tgt_func inside the wrapper. So, the defaults need
        # to be removed.
        signature = inspect.formatargspec(
                formatvalue=lambda val: "",
                *newargspec
                )[1:-1]

        # Defaults for our four new arguments that will go in the wrapper.
        newdefaults = argspec[3] + (None, None, None, False)
        newargspec = argspec[0:3] + (newdefaults,)

        # Add the new arguments to the argspec
        newargspec = (newargspec[0] + ['zdesk_email', 'zdesk_password', 'zdesk_url', 'zdesk_token'],) + newargspec[1:]

        # Text version of the arguments with their defaults
        newsignature = inspect.formatargspec(*newargspec)[1:-1]

        # Add the annotations for the new arguments to the annotations that were passed in
        self.ann.update(dict(
             zdesk_email=("zendesk login email", "option", None, None, None, "EMAIL"),
             zdesk_password=("zendesk password or token", "option", None, None, None, "PW"),
             zdesk_url=("zendesk instance URL", "option", None, None, None, "URL"),
             zdesk_token=("specify if password is a zendesk token", "flag", None, bool),
        ))

        # Define and exec the wrapping function that will be returned
        new_func = (
                'def _wrapper_(%(newsignature)s):\n'
                '    config["zdesk_email"] = zdesk_email\n'
                '    config["zdesk_password"] = zdesk_password\n'
                '    config["zdesk_url"] = zdesk_url\n'
                '    config["zdesk_token"] = zdesk_token\n'
                '    return %(tgt_func)s(%(signature)s)\n' %
                {'signature':signature, 'newsignature':newsignature, 'tgt_func':'tgt_func'}
            )
        evaldict = {'tgt_func' : tgt_func, 'plac' : plac, 'config' : self.__config}
        if sys.version >= '3':
            exec(new_func, evaldict)
        else:
            exec new_func in evaldict
        wrapped = evaldict['_wrapper_']

        # Update the wrapper with all of the information from the wrapped function
        wrapped.__name__ = name
        wrapped.__doc__ = tgt_func.__doc__
        wrapped.func_defaults = newdefaults
        wrapped.__module__ = tgt_func.__module__
        wrapped.__dict__ = tgt_func.__dict__

        # Add the complete annotations to the wrapper function, and also add the getconfig method
        # so that the new arguments can be retrieved inside the wrapped function.
        # This must come after the __dict__ assignment
        wrapped.__annotations__ = self.ann
        wrapped.getconfig = self.getconfig
        self.wrapped = wrapped
        return wrapped

    def getconfig(self, section=None):
        """
        This method provides a way for decorated functions to get the
        four new configuration parameters *after* it has been called.

        If no section is specified, then the fully resolved zdesk
        config will be returned. That is defaults, zdesk ini section,
        command line options.

        If a section is specified, then the same rules apply, but also
        any missing items are filled in by the zdesk section. So the
        resolution is defaults, zdesk ini section, specified section,
        command line options.
        """
        if not section:
            return self.__config.copy()

        cmd_line = {}
        for k in self.__config:
            v = self.wrapped.plac_cfg.get(k, 'PLAC__NOT_FOUND')
            if v != self.__config[k]:
                # This config item is different when fully resolved
                # compared to the ini value. It was specified on the
                # command line.
                cmd_line[k] = self.__config[k]

        # Get the email, password, url, and token config from the indicated
        # section, falling back to the zdesk config for convenience
        cfg = {
            "zdesk_email": self.wrapped.plac_cfg.get(section + '_email',
                self.__config['zdesk_email']),
            "zdesk_password": self.wrapped.plac_cfg.get(section + '_password',
                self.__config['zdesk_password']),
            "zdesk_url": self.wrapped.plac_cfg.get(section + '_url',
                self.__config['zdesk_url']),
            "zdesk_token": self.wrapped.plac_cfg.get(section + '_token',
                self.__config['zdesk_token']),
        }

        # The command line trumps all
        cfg.update(cmd_line)

        return cfg

def call(obj, config=os.path.join(os.path.expanduser('~'), '.zdeskcfg'), section=None):
    plac_ini.call(obj, config=config, default_section=section)

