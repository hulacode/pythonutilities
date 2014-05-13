# The MIT License (MIT)
# Copyright (C) 2014 Hulacode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import argparse

parser = argparse.ArgumentParser(description='Looks at current directory, prunes files.')
parser.add_argument('-d','--directory',help='Directory to scan"',required=True)
parser.add_argument('-k','--keepfiles',help='Number of files to keep',required=True)
args = vars(parser.parse_args())
WorkingDirectory = args['directory']
KeepFiles = int(args['keepfiles'])

def PruneDirectory(directory, keepFiles):
    contents = os.listdir(directory)
    files = []
    allfiles = []
    deletefiles = []
    for c in contents:
        if os.path.isfile(os.path.join(directory,c)):
            files.append(os.path.join(directory,c))
    files.sort(key=lambda x: os.path.getmtime(x))
    for f in files:
        if f != __file__:
            print(f)
            allfiles.append(f)

    if len(allfiles) > keepFiles:
        deleteQuantity = len(allfiles) - keepFiles
        for a in allfiles:
            if (len(deletefiles) < deleteQuantity):
                deletefiles.append(a)
        print('marked for deletion:')
        for d in deletefiles:
            print("Deleting " + d)
            os.remove(d)
    else:
        print("No files to delete: " + str(len(allfiles)) + " files total, " + str(keepFiles) + " did not delete.")


if __name__ == "__main__":
    PruneDirectory(WorkingDirectory, KeepFiles)
