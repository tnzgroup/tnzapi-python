from setuptools import setup, find_packages
#from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='tnzapi',
    version='2.4.0.0',
    description='TNZ REST API Helper Library for Python',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony",
        'Operating System :: OS Independent'
    ],
    url='https://www.tnz.co.nz',
    author='TNZ Group Limited',
    author_email='support@tnz.co.nz',
    keywords=['tnz', 'api', 'sms', 'fax', 'email', 'voice', 'tts'],
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests'
        ],
    include_package_data=True,
    zip_safe=False
)
