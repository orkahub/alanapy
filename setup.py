from setuptools import setup

setup(
    name='alanapy',
    packages=['alanapy'],
    version='0.1',
    license='MIT',
    author = 'Orkahub Energy',
	author_email = 'orkahub@gmail.com',
	url = 'https://github.com/orkahub/alanapy',
    download_url = 'https://github.com/orkahub/alanapy/archive/v_01.tar.gz',
    description='Script for Alana API connection and functions [https://alana.tech/open/accounts/login]',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords= ['RESERVOIR', 'ENERGY', 'OIL', 'GAS', 'PRODUCTION', 'PYTHON',"ALANA"],
    install_requires=[
        'requests',
        'matplotlib',
        'numpy',
        'pandas',
		'datetime',
		'os',
		're'
    ],
)
