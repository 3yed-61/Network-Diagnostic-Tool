from setuptools import setup, find_packages

setup(
    name="network_diagnostic",
    version="3.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'wxPython>=4.2.0',
        'ping3>=4.0.3',
        'matplotlib>=3.5.2',
        'psutil>=5.9.0',
        'requests>=2.28.1',
        'ipaddress>=1.0.23'
    ]
) 