from setuptools import setup, find_packages


setup(
    name='txtulip',
    version='0.0.1',
    license='MIT',
    description='Run Twisted on the Tulip/asyncio event loop',
    url='https://github.com/itamarst/txtulip',
    packages=find_packages(),
    include_package_data=True,
    zip_zafe=False,
    platforms=['Any'],
)
