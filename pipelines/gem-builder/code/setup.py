from setuptools import setup, find_packages
setup(
    name = 'gem-builder',
    version = '1.0',
    packages = find_packages(include = ('gembuilder*', )) + ['prophecy_config_instances'],
    package_dir = {'prophecy_config_instances' : 'configs/resources/config'},
    package_data = {'prophecy_config_instances' : ['*.json', '*.py', '*.conf']},
    description = 'workflow',
    install_requires = [
'opensearch-py', 'boto3==1.28.62', 'pdf2image', 'unstructured==0.7.4', 'prophecy-libs==1.7.3'],
    entry_points = {
'console_scripts' : [
'main = gembuilder.pipeline:main'], },
    data_files = [(".prophecy", [".prophecy/workflow.latest.json"])],
    extras_require = {
'test' : ['pytest', 'pytest-html'], }
)
