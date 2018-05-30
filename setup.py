from setuptools import setup, find_packages

long_desc = '''
This package contains the examplecode Sphinx extension.
This extension adds support for a multiple language code block
widget to Sphinx.
'''

requires = ['Sphinx>=1.0']

setup(
    name='exec-block',
    version='0.1.0',
    license='BSD',
    author='Joris Gillis',
    description='Sphinx "exec-block" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
