from setuptools import setup, find_packages
version = open('VERSION').read().strip()

setup(
    name='pywebdriver',
    version=version,
    author='Akretion',
    author_email='contact@akretion.com',
    url='https://github.com/akretion/pywebdriver/',
    description='Python Web Services to communicate wih Devices',
    license="AGPLv3+",
    long_description=open('README.md').read(),
    package_dir={'pywebdriver': '.'},
    packages=[
        'pywebdriver',
        'pywebdriver.libraries',
        'pywebdriver.libraries.escpos',
    ],
    install_requires=[ r.strip() for r in open('requirement.txt').read().splitlines() ],
    package_data={'pywebdriver': [
        'templates/*.html',
        'static/images/*.png',
        'translations/*/*/*',
    ]},
    entry_points={
        'console_scripts': [
            'pywebdriverd = pywebdriver.pywebdriver:main',
    ]},
    include_package_data=True,
    zip_safe=False
)
