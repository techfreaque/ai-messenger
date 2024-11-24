import argparse

from app import main


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the application")
    parser.add_argument(
        '--dev-mode', action='store_true', help='Enable development mode'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(dev_mode=args.dev_mode)
