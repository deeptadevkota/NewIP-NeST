# SPDX-License-Identifier: Apache-2.0-only
# Copyright (c) 2019-2022 @deeptadevkota @shashank68

from setuptools import setup, find_packages

setup(
    name="New_IP",
    packages=find_packages(),
    install_requires=["nest @ git+https://gitlab.com/nitk-nest/nest.git"],
)
