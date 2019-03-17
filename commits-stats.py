#!/usr/bin/env python3

import argparse
import sys

def main(argv):
  parser = argparse.ArgumentParser(description='Produces commits history for given period')
  parser.add_argument('--repo-path', required=True)
  parser.add_argument('--authors', nargs='*', help='List of commits authors to process')
  parser.add_argument('--start-date')
  parser.add_argument('--end-date')
  options = parser.parse_args()
  print('Options: {}'.format(options))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))