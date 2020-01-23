import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.readlines()

setuptools.setup(
    name='ipmon',
    version='0.0.1',
    description='Poll hosts via ICMP to check on health',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author='Mitch Gates',
    author_email='gates55434@gmail.com',
    url='https://github.com/mistergates/ipmon',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    python_requires='>=3.4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
 