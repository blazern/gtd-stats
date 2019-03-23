import subprocess

# If stdout is not specified, the command will be also printed
def check_call(cmd, stdout=None):
  if stdout is None:
    print('### Executing cmd: {}\n'.format(cmd))
  subprocess.check_call(cmd, shell=True, stdout=stdout)

def check_output(cmd, print_cmd=True):
  if print_cmd:
    print('### Executing cmd: {}\n'.format(cmd))
  return subprocess.check_output(cmd, encoding='UTF-8', shell=True)