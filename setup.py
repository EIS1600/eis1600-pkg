#!/usr/bin/env python

from setuptools import setup

setup(name='EIS1600',
      version='0.1.0',
      description='EIS1600 project tools and utilities',
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=['eis1600',
                'eis1600.mui_handling',
                'eis1600.mui_handling.test'],
      scripts=['eis1600/bin/disassemble_into_mui_files.py', 'eis1600/bin/reassemble_from_mui_files.py'],
      package_data={'eis1600': ['templates/yaml_template.yml']},
      python_requires='>=3.7',
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
