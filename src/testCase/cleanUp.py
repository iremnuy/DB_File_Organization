# delete all txt files in this root directory

import os
import glob

for file in glob.glob("*.txt"):
    if file != "input.txt":
        os.remove(file)