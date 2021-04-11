from setuptools import setup, find_packages

setup(
    name='doctool',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click @ git+https://github.com/MarcelRobitaille/click',
        'colorama',
    ],
    entry_points='''
        [console_scripts]
        doctool=doctool.main:main
    ''',
)
