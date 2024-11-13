import argparse
import os
import xml.etree.ElementTree as ET

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

def main():
    args = parse_args()
    if not os.path.exists(args.tar):
        print(f"Tar file {args.tar} does not exist")
        exit(1)

if __name__ == "__main__":
    main()
