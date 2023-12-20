from setuptools import setup, find_packages
setup(
    name = 'data_vectorize',
    version = '1.0',
    packages = find_packages(include = ('data_vectorize*', )) + ['prophecy_config_instances'],
    package_dir = {'prophecy_config_instances' : 'configs/resources/config'},
    package_data = {'prophecy_config_instances' : ['*.json', '*.py', '*.conf']},
    description = 'workflow',
    install_requires = [
'opensearch-py', 'boto3==1.28.62', 'pdf2image', 'unstructured==0.7.4', 'prophecy-libs==1.7.3'],
    entry_points = {
'console_scripts' : [
'main = data_vectorize.pipeline:main'], },
    data_files = [(".prophecy", [".prophecy/workflow.latest.json"])],
    extras_require = {
'test' : ['pytest', 'pytest-html'], }
)
