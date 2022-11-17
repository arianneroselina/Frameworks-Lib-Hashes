import sys
import csv
import glob
from os.path import exists
import subprocess

flutter_file = 'libflutter.so'
react_native_file = 'libreact*.so'

flutter_folders = ['arm64-v8a', 'armeabi-v7a', 'x86_64']
react_native_folders = flutter_folders + ['x86']

# get the hash of libflutter.so file from arm64_v8a, armeabi_v7a, and x86_64 folders, then write them in the
# corresponding .csv files.
def hash_flutter(version, path):
    path = add_slash_to_path(path)

    for folder in flutter_folders:
        csv_file = f'files/flutter/{folder}.csv'
        try:
            output = subprocess.check_output(one_file_command(path + folder + '\\' + flutter_file)).decode("utf-8")

            start_index = output.find('so:') + 3
            end_index = output.find('CertUtil', start_index)
            output_hash = output[start_index+1: end_index].strip()

            finish = False
            versions_list = []

            if exists(csv_file):
                with open(csv_file, 'r') as csv_read:
                    csv_reader = csv.reader(csv_read)
                    for row in csv_reader:
                        change = False
                        for i in range(len(row)):
                            if change:
                                row[i] = output_hash
                                change = False
                                finish = True
                            if row[i] == version:
                                change = True
                        if len(row) != 0:
                            versions_list.append(row)

                with open(csv_file, 'w', newline='') as csv_write:
                    writer = csv.writer(csv_write)
                    writer.writerows(versions_list)

            if not finish:
                with open(csv_file, 'a') as csv_append:
                    csv_append.write(version + ',' + output_hash)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


# get the hash of libreact*.so file from arm64_v8a, armeabi_v7a, x86, and x86_64 folders, then write them in the
# corresponding .csv files.
def hash_react_native(version, react_native_files):
    for filepath in react_native_files:
        splitted = str(filepath).split('\\')
        filename = splitted[len(splitted)-1]

        for folder in react_native_folders:
            csv_file = f'files/react_native/{folder}.csv'
            try:
                output = subprocess.check_output(one_file_command(filepath)).decode("utf-8")

                start_index = output.find('so:') + 3
                end_index = output.find('CertUtil', start_index)
                output_hash = output[start_index + 1: end_index].strip()

                finish = False
                versions_list = []

                if exists(csv_file):
                    with open(csv_file, 'r') as csv_read:
                        csv_reader = csv.reader(csv_read)
                        for row in csv_reader:
                            change = False
                            for i in range(len(row)):
                                if change:
                                    row[i] = output_hash
                                    change = False
                                    finish = True
                                if row[i] == version and row[i+1] == filename:
                                    change = True
                            if len(row) != 0:
                                versions_list.append(row)

                    with open(csv_file, 'w', newline='') as csv_write:
                        writer = csv.writer(csv_write)
                        writer.writerows(versions_list)

                if not finish:
                    with open(csv_file, 'a') as csv_append:
                        csv_append.write(f'{version},{filename},{output_hash}')

            except subprocess.CalledProcessError as e:
                    raise RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


def one_file_command(filename):
    return 'certutil -hashfile \"' + filename + '\" SHA256'


def multiple_files_command(path, filename):
    return f'cd {path} && for %F in ({filename}) do @certutil -hashfile \"%F\" SHA256'


def add_slash_to_path(path):
    if not path.endswith('\\'):
        path += '\\'
    return path


def compare_versions(version1: str, version2: str):
    split1 = version1.split('.')
    split2 = version2.split('.')
    if split1[0] < split2[0]:
        return -1
    elif split1[0] > split2[0]:
        return 1
    elif split1[0] == split2[0]:
        if split1[1] < split2[1]:
            return -1
        elif split1[1] > split2[1]:
            return 1
        elif split1[1] == split2[1]:
            if split1[2] < split2[2]:
                return -1
            elif split1[2] > split2[2]:
                return 1
            elif split1[2] == split2[2]:
                return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception(f'Please specify the flutter version and the lib path!'
                        f'Expected 2 arguments, but was {len(sys.argv)}.\n'
                        f'Make sure there are no spaces in the path.')

    path = add_slash_to_path(sys.argv[2])

    if exists(path + flutter_folders[0] + '\\' + flutter_file):
        hash_flutter(sys.argv[1], sys.argv[2])

    if glob.glob(path + react_native_folders[0] + '\\' + react_native_file):
        hash_react_native(sys.argv[1], glob.glob(path + react_native_folders[0] + '\\' + react_native_file))
