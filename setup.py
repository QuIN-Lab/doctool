from setuptools import setup, find_packages

setup(
    name='doctool',
    version='0.1.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'rich',
        'pdoc3',
        'pathos',
        'timer',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        doctool=doctool.main:main
    ''',
)
