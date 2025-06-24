from setuptools import setup, find_packages

setup(
    name="minifetch-tool",
    version="1.0.0.post1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['ascii/*.txt', 'custom.txt'],
    },
    install_requires=[
        'colorama',
        'psutil',
        'distro; platform_system=="Linux"',
    ],
    entry_points={
        'console_scripts': [
            'minifetch=minifetch:entry_point',
        ],
    },
    author="wdkq",
    author_email="koc2b93o0@mozmail.com",
    description="A mini system information fetch tool.",
    license="MIT",
    keywords="system info fetch",
    url="https://github.com/widikov/minifetch",
)
