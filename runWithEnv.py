import sys, os, venv, subprocess, shutil


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    args = sys.argv[1:]
    reinstall = False

    for i, arg in enumerate(args):
        if arg == "-reinstall":
            reinstall = True
            args.pop(i)
        if arg == "-h" or arg == "--h" or arg == "h":
            help_msg()
            return()
    if len(args) < 2:
        print("not enough arguments given.")
        help_msg()
        return()
    else:
        env_name = args[0]
        env_path = os.path.join(root_dir, env_name)
        run_file = args[1]
        module_file = None
    if len(args) > 2:
        module_file = os.path.join(root_dir, args[2])
    py_exec = os.path.join(env_path, "Scripts", "python.exe")

    if reinstall:
        if os.path.exists(env_path):
            print("Removing old installation ...")
            # renaming first to free up the path immediately, since removing takes a while
            to_remove = os.path.join(root_dir, "."+env_name)
            os.rename(env_path, to_remove)
            shutil.rmtree(to_remove)

    if not os.path.exists(env_path):
        print("Setting up environment (this might take a few minutes) ...")
        venv.create(env_path, with_pip=True)

        if module_file:
            print("Installing modules ...")
            subprocess.run([py_exec, '-m', 'pip', 'install', '-r', module_file])

    print("starting executable")
    subprocess.run([py_exec, run_file])


def help_msg():
    print("arg1 = environment folder name")
    print("arg2 = File to be ran")
    print("arg3 (optional) = file with names of modules to be installed")
    print("-reinstall anywhere to remove the folder first and reinstall the environment")


if __name__ == '__main__':
    main()