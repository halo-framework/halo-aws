from distutils.core import setup

# pip install halolib-1.0.1.zip
# python setup.py sdist --formats=zip
# \dev\python27\python setup.py build
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='halolib',
    version='0.13.6',
    packages=['halolib', 'halolib.flask'],
    url='https://github.com/yoramk2/halolib',
    license='MIT License',
    author='yoramk2',
    author_email='yoramk2@yahoo.com',
    description='this is the Halo framework library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
