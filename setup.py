from setuptools import setup, find_packages

setup(
    name='doctool',
    version='0.0.3',
    packages=find_packages(),
    package_data = {
        'cli_documentation': ['*.tex'],
    },
    install_requires=[
        'click @ git+https://github.com/MarcelRobitaille/click',
        'colorama',
        'pdoc3',
    ],
    entry_points='''
        [console_scripts]
        doctool=doctool.main:main
    ''',
)
