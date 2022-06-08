import setuptools

with open('README.md', 'r') as f:
    long_desc = f.read()

# get __version__
exec(open('lifespec_fl/_version.py').read())

setuptools.setup(
    name='lifespec_fl',
    version = __version__,
    author='Brian Carlsen',
    author_email = 'carlsen.bri@gmail.com',
    description = '.',
    long_description = long_desc,
    long_description_content_type = 'text/markdown',
    keywords = ['lifespec', '.fl', 'fl', 'file'],
    url = 'https://github.com/bicarlsen/lifespec_fl.git',
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'setuptools',
        'pyyaml',
        'numpy',
        'pandas',
        'parse-binary-file>=0.0.2'
    ],
    package_data = {
        'lifespec_fl': ['data/*']
    },
    entry_points = {
        'console_scripts': [
            'lifespec_fl=lifespec_fl.__main__:_main'
        ]
    }
)
