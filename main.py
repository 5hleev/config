import argparse
import os
import xml.etree.ElementTree as ET
import tarfile

def parse_args():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--tar', required=True, help='Path to the tar file')
    parser.add_argument('--log', required=True, help='Path to the log file')
    return parser.parse_args()

def log_action(log_file, command, description):
    action = ET.SubElement(log_file, "action")
    action.set("command", command)
    action.text = description

def exit_shell(log_file, log_file_path):
    log_action(log_file, "exit", "Exiting shell")
    save_log(log_file_path, log_file)
    exit(0)

def save_log(log_file_path, log_file=None):
    if log_file is not None:
        tree = ET.ElementTree(log_file)
        tree.write(log_file_path)

def list_directory(current_path, tar_file, log_file):
    current_path = current_path.strip('/')
    current_path_len = len(current_path)
    for file in tar_file.getnames():
        if file.startswith(current_path):
            relative_path = file[current_path_len:].lstrip('/')
            if relative_path and '/' not in relative_path:
                print(relative_path)
                log_action(log_file, "ls", f"Listed {relative_path}")

def change_directory(current_path, target_directory, tar_file, log_file):
    if target_directory == "/":
        new_dir = "/root"
    elif target_directory.startswith("/"):
        new_dir = "/root" + target_directory.strip('/')
    else:
        new_dir = os.path.join(current_path, target_directory).replace("\\", "/").strip('/')

    if any(f.startswith(new_dir + '/') for f in tar_file.getnames()):
        log_action(log_file, "cd", f"Changed directory to {new_dir}")
        return new_dir
    else:
        print(f"cd: no such file or directory: {target_directory}")
        log_action(log_file, "cd", f"Failed to change directory to {target_directory}")
        return current_path

def tree(current_path, tar_files, log_file, indent=0):
    prefix = " " * indent
    sub_dirs = {}
    for file in tar_files:
        if file.startswith(current_path.lstrip("/")):
            relative_path = file[len(current_path):].lstrip('/').split('/')
            if len(relative_path) > 1:
                sub_dir = relative_path[0]
                if sub_dir not in sub_dirs:
                    sub_dirs[sub_dir] = []
                sub_dirs[sub_dir].append(file)
    for file in tar_files:
        if file.startswith(current_path.lstrip("/")):
            relative_path = file[len(current_path):].lstrip('/').split('/')
            if relative_path[0] not in sub_dirs and relative_path[0] != "":
                print(f"{prefix}{relative_path[0]}")
                log_action(log_file, "tree", f"Displayed {relative_path[0]}")
    for sub_dir, files in sub_dirs.items():
        print(f"{prefix}{sub_dir}/")
        log_action(log_file, "tree", f"Displayed {sub_dir}/")
        tree(f"{current_path}/{sub_dir}".rstrip('/'), files, log_file, indent + 4)

def du(current_path, tar_file, log_file):
    size = 0
    for member in tar_file.getmembers():
        if member.name.startswith(current_path.strip('/')):  # Ensure the path is correctly processed
            size += member.size
    print(f"{current_path}: {size} bytes")
    log_action(log_file, "du", f"Calculated size of {current_path}: {size} bytes")

def find(current_path, filename, tar_file, log_file):
    found_files = [name for name in tar_file.getnames() if
                   name.startswith(current_path.strip('/')) and filename in os.path.basename(name)]
    if found_files:
        for file in found_files:
            print(file)
            log_action(log_file, "find", f"Found file {file}")
    else:
        print(f"find: {filename} not found")
        log_action(log_file, "find", f"File {filename} not found")

def run_shell(tar, log_file_path):
    current_path = "/root"
    log_file = ET.Element("session")

    # Если лог-файл не существует, создаем пустой XML для лога
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as log_file:
            log_file.write('<session></session>')

    try:
        with tarfile.open(tar, "r") as tar_file:
            while True:
                command = input(prompt(current_path)).strip().split()
                if not command:
                    continue
                cmd = command[0]

                if cmd == 'exit':
                    exit_shell(log_file, log_file_path)
                elif cmd == 'ls':
                    if len(command) == 1:
                        list_directory(current_path, tar_file, log_file)
                    else:
                        print("ls: arguments are not supported")
                elif cmd == 'cd':
                    if len(command) == 2:
                        current_path = change_directory(current_path, command[1], tar_file, log_file)
                    elif len(command) == 1:
                        print("cd: missing argument")
                    else:
                        print("cd: too many arguments")
                elif cmd == 'tree':
                    tree(current_path, tar_file.getnames(), log_file)
                elif cmd == 'du':
                    if len(command) == 1:
                        du(current_path, tar_file, log_file)
                    else:
                        print("du: arguments are not supported")
                elif cmd == 'find':
                    if len(command) == 2:
                        find(current_path, command[1], tar_file, log_file)
                    else:
                        print("find: usage: find <filename>")
                else:
                    print(f"{cmd}: command not found")

                save_log(log_file_path, log_file)
    except Exception as e:
        print(f"Error occurred: {e}")

def prompt(current_path):
    home_path = "/root"
    if current_path == home_path:
        path_display = "~"
    else:
        path_display = current_path.lstrip('/')
    return f"emulator:{path_display}$ "

def main():
    args = parse_args()
    if not os.path.exists(args.tar):
        print(f"Tar file {args.tar} does not exist")
        exit(1)
    run_shell(args.tar, args.log)

if __name__ == "__main__":
    main()
