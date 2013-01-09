
from distutils.core import setup

setup(
    url='none',
    author='Matt Haggard',
    author_email='haggardii@gmail.com',
    name='garden',
    version='0.0.1',
#    scripts=['bin/garden'],
    packages=[
        'garden', 'garden.test',
        'twisted.plugins',
    ],
    install_requires=[
        'Twisted>=12.0.0',
    ],
)
