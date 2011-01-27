from setuptools import setup, find_packages

setup(
    name = "foursquare",
    version = "1.0",
    url = 'https://github.com/alfredo/foursquare-api',
    license = 'BSD',
    description = "Simple wrapper around foursquare v2 API.",
    author = 'Alfredo Aguirre',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
