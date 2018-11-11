from distutils.core import setup

# pip install halolib-1.0.1.zip
# python setup.py sdist --formats=zip
# \dev\python27\python setup.py build

setup(
    name='halolib',
    version='0.13.5',
    packages=['halolib', 'halolib.flask'],
    url='',
    license='MIT License',
    author='yoramk2',
    author_email='yoramk2@yahoo.com',
    description='this is the Halo framework library',
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
        'Framework :: Flask :: 1.0',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
