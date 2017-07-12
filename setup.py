import setuptools

setuptools.setup(
    name="djver",
    version="2.1.0",
    url="https://github.com/sesh/djver",

    author="Brenton Cleeland",
    author_email="brenton@brntn.me",

    description="Ever wanted to know what version of Django someone else is running?",

    packages=setuptools.find_packages(),
    install_requires=['requests', 'docopt'],

    entry_points={
        'console_scripts': [
            'djver = djver.djver:djver',
        ]
    },

    classifiers=[
        # 'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
