from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='eis1600',
      version='1.2.1',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=find_packages(include=['eis1600', 'eis1600.*'], exclude=['excluded']),
      package_data={'eis1600.gazetteers.data': ['*.csv'], 'eis1600.helper.data': ['*.csv']},
      entry_points={
          'console_scripts': [
                  'analyse_all_on_cluster = eis1600.corpus_analysis.analyse_all_on_cluster:main [EIS]',
                  'annotate_goldstandard = eis1600.nlp.annotate_goldstandard:main [NER]',
                  'annotate_mius = eis1600.nlp.ner_annotate_mius:main [NER]',
                  'annotate_topd = eis1600.helper.annotate_topd:main [NER]',
                  'btopd_to_bio = eis1600.helper.btopd_to_bio:main',
                  'convert_mARkdown_to_EIS1600TMP = eis1600.markdown.convert_mARkdown_to_EIS1600TMP:main',
                  'count_tokens_per_miu = eis1600.statistics.count_tokens_per_miu:main',
                  'disassemble_into_miu_files = eis1600.miu.disassemble_into_miu_files:main',
                  'eval_date_model = eis1600.helper.eval_date_model:main [EVAL]',
                  'eval_topo_cat_model = eis1600.helper.eval_topo_cat_model:main [EVAL]',
                  'fix_ono_p_tags_order = eis1600.helper.fix_ono_p_tags_order:main',
                  'fix_miu_annotation = eis1600.helper.fix_miu_annotation:main',
                  'generate_autoreport = eis1600.helper.generate_autoreport:main',
                  'insert_uids = eis1600.markdown.insert_uids:main',
                  'miu_random_revisions = eis1600.helper.miu_random_revisions:main',
                  'miu_stats = eis1600.stats.miu_stats:main',
                  'onomastic_annotation = eis1600.onomastics.annotation:main',
                  'q_tags_to_bio = eis1600.helper.q_tags_to_bio:main',
                  'reassemble_from_miu_files = eis1600.miu.reassemble_from_miu_files:main',
                  'sheets_topod_stats = eis1600.helper.sheets_topod_stats:main',
                  'topo_tags_to_bio = eis1600.helper.topo_tags_to_bio:main',
                  'topod_extract_incomplete = eis1600.helper.topod_extract_incomplete:main',
                  'topod_extract_places_regex = eis1600.helper.topod_extract_places_regex:main',
                  'topod_insert_into_miu = eis1600.helper.topod_insert_into_miu:main',
                  'toponym_annotation = eis1600.toponyms.annotation:main',
                  'update_uids = eis1600.markdown.update_uids:main',
                  'xx_update_uids_old_process = eis1600.markdown.update_uids_old_process:main',
                  'yml_to_json = eis1600.helper.yml_to_json:main'
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
