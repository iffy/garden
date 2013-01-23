
from distutils.core import setup

setup(
    url='https://github.com/iffy/garden',
    author='Matt Haggard',
    author_email='haggardii@gmail.com',
    name='garden',
    version='0.0.1',
#    scripts=['bin/garden'],
    packages=[
        'garden', 'garden.test',
        'garden.twistd', 'garden.twistd.test',
        'twisted.plugins',
    ],
    install_requires=[
        'Twisted>=12.3.0',
    ],
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))

