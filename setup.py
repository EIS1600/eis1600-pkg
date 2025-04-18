from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='eis1600',
      version='1.7.4',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=find_packages(include=['eis1600', 'eis1600.*'], exclude=['excluded']),
      package_data={
              'eis1600.gazetteers.data': ['*.csv'],
              'eis1600.markdown.data': ['*.csv'],
              'eis1600.models.data': ['*.csv'],
              'eis1600.processing.persistent_ids': ['long_short_ids_mapping.json',
                                                    'deprecated_long_short_ids_mapping.json']
      },
      entry_points={
          'console_scripts': [
                  'analyse_all_on_cluster = eis1600.corpus_analysis.analyse_all_on_cluster:main [EIS]',
                  'analyse_text = eis1600.corpus_analysis.analyse_text:main [EIS]',
                  'annotate_topd = eis1600.toponym_descriptions.annotate_topd:main [NER]',
                  'btopd_to_bio = eis1600.toponym_descriptions.btopd_to_bio:main',
                  'check_formatting = eis1600.texts_to_mius.check_formatting:main',
                  'check_mius = eis1600.texts_to_mius.check_mius:main',
                  'clean_ids_mapping = eis1600.processing.short_miu_generation:clean_unused_old_ids',
                  'convert_mARkdown_to_EIS1600TMP = eis1600.texts_to_mius.convert_mARkdown_to_EIS1600TMP:main',
                  'count_tokens_per_miu = eis1600.statistics.count_tokens_per_miu:main',
                  'eval_date_model = eis1600.model_evaluations.eval_date_model:main [EVAL]',
                  'eval_topo_cat_model = eis1600.model_evaluations.eval_topo_cat_model:main [EVAL]',
                  'ids_insert_or_update = eis1600.texts_to_mius.ids_insert_or_update:main',
                  'incorporate_newly_prepared_files_in_corpus = '
                      'eis1600.texts_to_mius.incorporate_newly_prepared_files_in_corpus:main',
                  'miu_random_revisions = eis1600.helper.miu_random_revisions:main',
                  'mius_count_categories = eis1600.statistics.count_categories:main',
                  'prepare_training_data = eis1600.bio.prepare_training_data:main',
                  'q_tags_to_bio = eis1600.bio.q_tags_to_bio:main',
                  'reannotation = eis1600.training_data.reannotation:main',
                  'reconstruct_texts = eis1600.json_to_text.reconstruct:main',
                  'sheets_topod_stats = eis1600.toponym_descriptions.topod_sheets_stats:main',
                  'show_input_files_sizes = eis1600.helper.files_sizes:main',
                  'split_mius_into_paragraphs = eis1600.paragraphs.split_mius_into_paragraphs:main [EIS]',
                  'topo_tags_to_bio = eis1600.bio.topo_tags_to_bio:main',
                  'topod_extract_incomplete = eis1600.toponym_descriptions.topod_extract_incomplete:main',
                  'topod_extract_places_regex = eis1600.toponym_descriptions.topod_extract_places_regex:main',
                  'topod_insert_into_miu = eis1600.toponym_descriptions.topod_insert_into_miu:main',
                  'tsv_dump = eis1600.json_to_tsv.corpus_dump:main',
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
              'requests',
              'ujson'
      ],
      extras_require={
              'NER': ['camel-tools', 'torch'],
              'EVAL': ['evaluate', 'seqeval', 'tensorflow'],
              'EIS': ['camel-tools', 'torch', 'torchvision', 'torchaudio', 'transformers']
      },
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
