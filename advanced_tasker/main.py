import argparse
from ui.cli.app import run_cli
from ui.tk.app import run_tk_app

def main():
    parser = argparse.ArgumentParser(description="Tasker System")
    parser.add_argument('--cli', action='store_true', help='Use command line interface')
    parser.add_argument('--tk', action='store_true', help='Use Tkinter GUI')
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_tk_app()

if __name__ == "__main__":
    main()