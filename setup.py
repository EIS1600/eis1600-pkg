from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='eis1600',
      version='0.2.8',
      description='EIS1600 project tools and utilities',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/EIS1600/eis1600-pkg',
      author='Lisa Mischer',
      author_email='mischer.lisa@gmail.com',
      license='MIT License',
      packages=['eis1600',
                'eis1600.helper',
                'eis1600.miu_handling',
                'eis1600.markdown'],
      scripts=['eis1600/bin/disassemble_into_miu_files.py',
               'eis1600/bin/reassemble_from_miu_files.py',
               'eis1600/bin/convert_mARkdown_to_EIS1600.py',
               'eis1600/bin/insert_uids.py',
               'eis1600/bin/update_uids.py'],
      package_data={'eis1600.miu_handling': ['yaml_template.yml']},
      python_requires='>=3.7',
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research']
      )
