from setuptools import setup, find_packages

version = open('VERSION').read().strip()
license = open('LICENSE').read().strip()

setup(
    name = 'pyerse',
    version = version,
    license = license,
    author = 'Diogo Gomes',
    author_email = 'diogogomes@gmail.com',
    url = 'http://github.com/dgomes/pyerse',
    description = 'Provides algorithms and an API for Portugal Energy Regulator (ERSE)',
    long_description = open('README.md').read().strip(),
    packages = find_packages(),
    install_requires=[
        # put packages here
    ],
    test_suite = 'tests',
    entry_points = {
	    'console_scripts': [
	        'packagename = packagename.__main__:main',
	    ]
	}
)
