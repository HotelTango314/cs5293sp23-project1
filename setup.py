from setuptools import setup, find_packages

setup(
        name = 'project1',
        version = '1.0',
        author = 'Henry Thomas',
        author_email = 'henry.r.thomas-1@ou.edu',
        packages = find_packages(exclude=('tests','docs')),
        setup_requires = ['pytest-runner'],
        tests_requires = ['pytest']
)
