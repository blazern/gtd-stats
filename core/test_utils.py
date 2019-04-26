import os
from datetime import datetime
from random import random

def make_file_and_write(dir_path, file_contents):
  file_name = str(random())
  file_path = os.path.join(dir_path, file_name)
  with open(file_path, "w") as text_file:
    text_file.write(file_contents)
  return file_path

def make_tmp_dir():
  dir_name = str(datetime.now().microsecond) + str(random())
  dir_path = os.path.join('/tmp/', dir_name)
  os.makedirs(dir_path)
  return dir_path