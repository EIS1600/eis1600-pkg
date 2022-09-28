from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='eis1600',
      version='0.2.0',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=['eis1600',
                'eis1600.mui_handling',
                'eis1600.eis1600_tags',
                'eis1600.dates',
                'eis1600.ara_re_pattern',
                'eis1600.preprocessing'],
      scripts=['eis1600/bin/disassemble_into_mui_files.py', 'eis1600/bin/reassemble_from_mui_files.py'],
      package_data={'eis1600.mui_handling': ['yaml_template.yml']},
      python_requires='>=3.7',
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
