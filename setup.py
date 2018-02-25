from setuptools import setup

setup(
    name='bh3',
    version='1.0.0',
    url='https://github.com/dzdx/bh3',
    author='dzdx',
    author_email='dzidaxie@gmail.com',
    description=('wow very terminal bh3'),
    license='MIT',
    packages=['bh3'],
    package_data={'bh3': ['ascii_imgs/*/*.txt']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    entry_points={'console_scripts': ['bh3 = bh3.core:main']},
)
