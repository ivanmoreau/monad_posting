from setuptools import find_packages, setup

setup(
    name='monad_posting',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    package_dir={"": "."},
    install_requires=[
        'flask',
        'sqlalchemy',
        'mysqlclient'
    ],
)