from setuptools import setup, find_packages

# Reading long description from README.md file
with open("README.md", "r") as fh:
    long_description = fh.read()

# Reading requirements from requirements.txt file
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='ApplicationTracker',  # Package name
    version='0.1.0',  # Start with an alpha version
    url='https://github.com/asheeque/ApplicationTracker',  # Your package's repository URL
    author='Asheeque',  # Your name
    author_email='asheeque.cm@gmail.com',  # Your email
    description='A package to track and analyze application emails.',  # Short description
    long_description=long_description,  # Long description read from README
    long_description_content_type="text/markdown",  # Specify markdown as content type
    packages=find_packages(exclude=["tests*"]),  # Automatically discover and include all packages in the package directory
    install_requires=required,  # List of dependencies read from requirements.txt
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Assuming you're using the MIT License
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7',  # Minimum version requirement of the package
    keywords='application tracker, email analysis',  # Keywords for your package
    include_package_data=True  # Includes any data files contained within your package directories
)
