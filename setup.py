try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pybioportal',
    version='0.1',
    description="A Python binding of the BioPortal REST API.",
    author='Lu\xc3\xads Campos',
    author_email='luis.filipe.lcampos@gmail.com',
    url='https://github.com/LLCampos/pybioportal',
    license='',
    install_requires=[
        'requests'
    ],
)
