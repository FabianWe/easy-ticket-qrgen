from setuptools import setup, find_packages
from easyticket_qrgen import __version__


from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easyticket_qrgen',
    version=__version__,
    description='Package for creating QR Codes for the event ticket system easy-ticket.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FabianWe/easyticket_qrgen',
    author='Fabian Wenzelmann',
    author_email='fabianwen@posteo.eu',
    license='Apache License 2.0',
    keywords='qr qr-code ticket event',
    packages=find_packages(exclude=('docs', 'py')),
    include_package_data=True,
    install_requires=['pyqrcode>=1.2.1', 'Pillow>=6.1'],
)
