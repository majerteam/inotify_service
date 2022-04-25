from distutils.core import setup
from setuptools import find_packages

entry_points = {"console_scripts": ["inotify-service-start = inotify_service:run"]}

with open("./requirements.txt", "r") as fbuf:
    requirements = fbuf.read().splitlines()

setup(
    name="inotify_service",
    version="1.0.0",
    description="Run scripts responding to inotify events",
    author="Gaston Tjebbes",
    author_email="g.t@majerti.fr",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Operating System :: Linux",
    ],
    python_requires=">=3.6",
    keywords="inotify incron asyncio",
    url="https://github.com/majerteam/inotify_service",
    packages=find_packages(),
    zip_safe=True,
    install_requires=requirements,
    entry_points=entry_points,
)
