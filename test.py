import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--bp', default='word_data/', type=str)
args = parser.parse_args()
print(args.bp)
