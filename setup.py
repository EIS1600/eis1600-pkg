from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='eis1600',
      version='0.6.4',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=['eis1600',
                'eis1600.dates',
                'eis1600.helper',
                'eis1600.markdown',
                'eis1600.miu',
                'eis1600.nlp'],
      entry_points={
          'console_scripts': [
                  'convert_mARkdown_to_EIS1600TMP = eis1600.markdown.convert_mARkdown_to_EIS1600TMP:main',
                  'disassemble_into_miu_files = eis1600.miu.disassemble_into_miu_files:main',
                  'insert_uids = eis1600.markdown.insert_uids:main',
                  'miu_random_revisions = eis1600.helper.miu_random_revisions:main',
                  'ner_annotate_mius = eis1600.nlp.ner_annotate_mius:main [NER]',
                  'reassemble_from_miu_files = eis1600.miu.reassemble_from_miu_files:main',
                  'update_uids = eis1600.markdown.update_uids:main',
                  'xx_update_uids_old_process = eis1600.markdown.update_uids_old_process:main'
          ],
      },
      python_requires='>=3.7, <3.9',
      install_requires=['openiti', 'pandas', 'tqdm', 'p_tqdm'],
      extras_require={'NER': ['camel-tools']},
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
