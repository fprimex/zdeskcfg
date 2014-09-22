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
        self.config = {}

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
             zdesk_email=("zendesk login email", "option", 'e', None, None, "EMAIL"),
             zdesk_password=("zendesk password or token", "option", 'p', None, None, "PASSWD"),
             zdesk_url=("zendesk instance URL", "option", 'u', None, None, "URL"),
             zdesk_token=("specify if password is a Zendesk token", "flag", 't'),
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
        evaldict = {'tgt_func' : tgt_func, 'plac' : plac, 'config' : self.config}
        exec new_func in evaldict
        wrapped = evaldict['_wrapper_']

        # Update the wrapper with all of the information from the wrapped function
        wrapped.__name__ = name
        wrapped.__doc__ = tgt_func.__doc__
        wrapped.func_defaults = newdefaults
        wrapped.__module__ = tgt_func.__module__
        wrapped.__dict__ = tgt_func.__dict__

        # Add the complete annotations to the wrapper functoin, and also add the getconfig method
        # so that the new arguments can be retrieved inside the wrapped function.
        # This must come after the __dict__ assignment
        wrapped.__annotations__ = self.ann
        wrapped.getconfig = self.getconfig
        return wrapped

    def getconfig(self):
        """
        This method provides a way for decorated functions to get the
        four new configuration parameters.
        """
        return self.config

def call(obj, config=os.path.join(os.path.expanduser('~'), '.zdeskcfg'), section=None):
    plac_ini.call(obj, config=config, default_section=section)

