from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='eis1600',
      version='1.2.7',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=find_packages(include=['eis1600', 'eis1600.*'], exclude=['excluded']),
      package_data={'eis1600.gazetteers.data': ['*.csv'], 'eis1600.markdown.data': ['*.csv']},
      entry_points={
          'console_scripts': [
                  'analyse_all_on_cluster = eis1600.corpus_analysis.analyse_all_on_cluster:main [EIS]',
                  'annotate_goldstandard = eis1600.nlp.annotate_goldstandard:main [NER]',
                  'annotate_mius = eis1600.nlp.ner_annotate_mius:main [NER]',
                  'annotate_topd = eis1600.toponym_descriptions.annotate_topd:main [NER]',
                  'btopd_to_bio = eis1600.toponym_descriptions.btopd_to_bio:main',
                  'convert_mARkdown_to_EIS1600TMP = eis1600.text_to_mius.convert_mARkdown_to_EIS1600TMP:main',
                  'count_tokens_per_miu = eis1600.statistics.count_tokens_per_miu:main',
                  'disassemble_into_miu_files = eis1600.miu.disassemble_into_miu_files:main',
                  'eval_date_model = eis1600.model_evaluations.eval_date_model:main [EVAL]',
                  'eval_topo_cat_model = eis1600.model_evaluations.eval_topo_cat_model:main [EVAL]',
                  'incorporate_newly_prepared_files_in_corpus = '
                  'eis1600.texts_to_mius.incorporate_newly_prepared_files_in_corpus:main',
                  'insert_uids = eis1600.text_to_mius.insert_uids:main',
                  'miu_random_revisions = eis1600.helper.miu_random_revisions:main',
                  'mius_count_categories = eis1600.statistics.count_categories:main',
                  'onomastic_annotation = eis1600.onomastics.annotation:main',
                  'q_tags_to_bio = eis1600.bio.q_tags_to_bio:main',
                  'reassemble_from_miu_files = eis1600.miu.reassemble_from_miu_files:main',
                  'sheets_topod_stats = eis1600.toponym_descriptions.topod_sheets_stats:main',
                  'topo_tags_to_bio = eis1600.bio.topo_tags_to_bio:main',
                  'topod_extract_incomplete = eis1600.toponym_descriptions.topod_extract_incomplete:main',
                  'topod_extract_places_regex = eis1600.toponym_descriptions.topod_extract_places_regex:main',
                  'topod_insert_into_miu = eis1600.toponym_descriptions.topod_insert_into_miu:main',
                  'toponym_annotation = eis1600.toponyms.annotation:main',
                  'update_uids = eis1600.texts_to_mius.update_uids:main',
                  'yml_to_json = eis1600.yml.yml_to_json:main'
          ],
      },
      python_requires='>=3.7',
      install_requires=[
              'openiti',
              'pandas',
              'numpy',
              'tqdm',
              'p_tqdm',
              'importlib_resources',
              'jsonpickle',
              'requests'
      ],
      extras_require={
              'NER': ['camel-tools', 'torch'],
              'EVAL': ['evaluate', 'seqeval', 'tensorflow'],
              'EIS': ['camel-tools', 'torch', 'torchvision', 'torchaudio']
      },
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
