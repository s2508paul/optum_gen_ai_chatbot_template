from setuptools import setup, find_packages
setup(
    name = 'optum-pdf-data-vectorize',
    version = '1.0',
    packages = find_packages(include = ('optumpdfdatavectorize*', )) + ['prophecy_config_instances'],
    package_dir = {'prophecy_config_instances' : 'configs/resources/config'},
    package_data = {'prophecy_config_instances' : ['*.json', '*.py', '*.conf']},
    description = 'workflow',
    install_requires = ['prophecy-spark-ai==0.1.11', 'pdf2image', 'opensearch-py', 'boto3==1.28.62', 'unstructured==0.7.4',
     'prophecy-libs==1.6.7'],
    entry_points = {
'console_scripts' : [
'main = optumpdfdatavectorize.pipeline:main'], },
    data_files = [(".prophecy", [".prophecy/workflow.latest.json"])],
    extras_require = {
'test' : ['pytest', 'pytest-html'], }
)
