import sys

from src.skyguard.evaluation.runner import run_evaluation


if __name__ == "__main__":
    print(run_evaluation(*sys.argv[1:]))
