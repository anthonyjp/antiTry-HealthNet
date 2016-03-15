import os
import zipfile
import pathlib
import argparse
import json
import sys

from subprocess import call, check_output, STDOUT
from HealthNet import settings

MANIFEST = 'MANIFEST.json'
ZIPNAME_TEMPLATE = 'dist/%s-%s.zip'

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

if settings.DEBUG:
    raise ValueError('Please set settings.DEBUG to False!')

if not os.path.exists(MANIFEST):
    raise FileNotFoundError('Missing Manifest: %s!' % MANIFEST)

def main():
    arguments = parser()
    args = vars(arguments.parse_args())
    nomigrate = args['nomigrate']

    with open('MANIFEST.json', 'r') as f:
        manifest = json.loads(f.read())

    verify_manifest(manifest)

    res = check_output(['python', 'manage.py', 'check', '--deploy'], stderr=STDOUT)
    print(res.decode(), file=sys.stderr)
    if not yes_no_prompt('The above is what should be verified before deploying. Please check the Django Deployment'
                         'Checklist as well! It\'s online! Continue?: ', file=sys.stderr):
        print('Exiting...')
        exit()

    zip_filename = ZIPNAME_TEMPLATE % (manifest['APP_NAME'], manifest['VERSION'])
    print('Creating project package: "%s" (This might take a while!)' % zip_filename)

    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    if not nomigrate:
        call(['python', 'manage.py', 'makemigrations'])
        call(['python', 'manage.py', 'migrate'])

    exclusion = manifest['EXCLUDES']
    manifest = manifest['INCLUDES']

    with zipfile.ZipFile(zip_filename, 'w') as z:
        for file in manifest['files']:
            z.write(file)
        for dir in manifest['dirs']:
            path = pathlib.Path(dir)
            positives = path.glob(manifest['dirs'][dir])
            for antiglob in exclusion['files']:
                for p in path.glob(antiglob):
                    positives = [x for x in positives if x != p]    # Very inefficient
            for p in positives:
                z.write(str(p))

    print("MAKE SURE TO SET DEBUG BACK TO TRUE FOR DEBUGGING!")


def parser():
    parser = argparse.ArgumentParser(
        description="Package entire project"
    )

    parser.add_argument('-n', '--no-migrate', action='store_true', dest='nomigrate',
                        help='If set then migrations are not attempted before packaging.')

    return parser


def yes_no_prompt(prompt, **kwargs):
    yes = {'yes', 'y', 'ok'}
    no = {'no', 'n', 'cancel'}

    while True:
        print(prompt, **kwargs, end='')
        ans = input().lower()

        if ans in yes:
            return True
        elif ans in no:
            return False
        else:
            print('Invalid choice!')


def verify_manifest(manifest_data):
    required = ['APP_NAME', 'VERSION', 'INCLUDES']

    for req in required:
        if req not in manifest_data:
            raise ValueError('MISSING MANIFEST VALUE: %s' % req)

if __name__ == '__main__':
    main()