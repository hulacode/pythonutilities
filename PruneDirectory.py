import os, sys, time
import argparse

parser = argparse.ArgumentParser(description='Looks at current directory, prunes files.')
parser.add_argument('-d','--directory',help='Directory to scan"',required=True)
parser.add_argument('-k','--keepfiles',help='Number of files to keep',required=True)
args = vars(parser.parse_args())
WorkingDirectory = args['directory'];
KeepFiles = int(args['keepfiles']);

def PruneDirectory(directory, keepFiles):
	contents = os.listdir(directory)
	files = []
	allfiles = []
	deletefiles = []
	for c in contents:
		if os.path.isfile(os.path.join(directory,c)):
			files.append(os.path.join(directory,c));
	files.sort(key=lambda x: os.path.getmtime(x))
	for f in files:
		if f != __file__:
			print(f);
			allfiles.append(f);
	
	if len(allfiles) > keepFiles:
		deleteQuantity = len(allfiles) - keepFiles;
		for a in allfiles:
			if (len(deletefiles) < deleteQuantity):
				deletefiles.append(a);
		print('marked for deletion:');
		for d in deletefiles:
			print("Deleting " + d);
			os.remove(d);				
	else:
		print("No files to delete: " + str(len(allfiles)) + " files total, " + str(keepFiles) + " did not delete.");
	
		
if __name__ == "__main__":
	PruneDirectory(WorkingDirectory, KeepFiles);
	
