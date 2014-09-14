#!/usr/bin/env python

from setuptools import setup

setup(
    author='Giovanni Torres Parra',
    author_email='fiatjaf@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        ],
    description='Client to a Micronalytics server',
    license='MIT',
    include_package_data=True,
    maintainer='Giovanni Torres Parra',
    maintainer_email='fiatjaf@gmail.com',
    name='microanalytics',
    py_modules=['microanalytics', 'charts'],
    install_requires=[
        'click>=3.3',
        'prettytable>=0.7.2',
        'requests>=2.4.1',
    ],
    url='https://github.com/fiatjaf/microanalytics',
    version='0.0.21',
    entry_points='''

    [console_scripts]
    microanalytics=microanalytics:main
    '''
)

