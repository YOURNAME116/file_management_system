import os
from datetime import datetime
import readline
class File:
    def __init__(self, name, content="", permissions="rw-"):
        self.name = name
        self.content = content
        self.created_time = datetime.now()
        self.modified_time = datetime.now()
        self.permissions = permissions

    def get_size(self):
        return len(self.content)

    def format_timestamp(self):
        return self.created_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_permissions(self):
        return self.permissions

    def chmod(self, permissions):
        self.permissions = permissions

    def write(self, content):
        if 'w' not in self.permissions:
            print(f"Permission denied: You don't have write permission for the file '{self.name}'.")
            return

        self.content = content
        self.modified_time = datetime.now()

class Folder:
    def __init__(self, name):
        self.name = name
        self.contents = []
        self.created_time = datetime.now()
        self.parent = None

    def get_size(self):
        total_size = 0
        for item in self.contents:
            if isinstance(item, File):
                total_size += item.get_size()
            elif isinstance(item, Folder):
                total_size += item.get_size()
        return total_size

    def format_timestamp(self):
        return self.created_time.strftime("%Y-%m-%d %H:%M:%S")

class FileSystem:
    def __init__(self):
        self.root = Folder("root")
        self.current_folder = self.root
        self.journal = []

    def run(self):
        while True:
            command = input("> ")
            parts = command.split(" ")
            if parts[0] == "ls":
                self.ls()
            elif parts[0] == "pwd":
                self.pwd()
            elif parts[0] == "cd":
                if len(parts) > 1:
                    self.cd(parts[1])
                else:
                    print("Missing folder name.")
            elif parts[0] == "cat":
                if len(parts) > 1:
                    self.cat(parts[1])
                else:
                    print("Missing file name.")
            elif parts[0] == "mkdir":
                if len(parts) > 1:
                    self.mkdir(parts[1])
                else:
                    print("Missing folder name.")
            elif parts[0] == "touch":
                if len(parts) > 1:
                    self.touch(parts[1])
                else:
                    print("Missing file name.")
            elif parts[0] == "rm":
                if len(parts) > 1:
                    self.rm(parts[1])
                else:
                    print("Missing file name.")
            elif parts[0] == "rmdir":
                if len(parts) > 1:
                    self.rmdir(parts[1])
                else:
                    print("Missing folder name.")
            elif parts[0] == "write":
                if len(parts) > 2:
                    self.write(parts[1], " ".join(parts[2:]))
                else:
                    print("Invalid command syntax. Usage: write <file> <content>")
            elif parts[0] == "cp":
                if len(parts) > 2:
                    self.cp(parts[1], parts[2])
                else:
                    print("Invalid command syntax. Usage: cp <source_file> <destination_file>")
            elif parts[0] == "mv":
                if len(parts) > 2:
                    self.mv(parts[1], parts[2])
                else:
                    print("Invalid command syntax. Usage: mv <source_file> <destination_file>")
            elif parts[0] == "size":
                if len(parts) > 1:
                    self.size(parts[1])
                else:
                    print("Missing file or folder name.")
            elif parts[0] == "chmod":
                if len(parts) > 2:
                    self.chmod(parts[1], parts[2])
                else:
                    print("Invalid command syntax. Usage: chmod <file> <permissions>")
            elif parts[0] == "journaling":
                self.journaling()
            elif parts[0] == "help":
                self.help()
            elif parts[0] == "exit":
                break
            else:
                print("Unknown command. Type 'help' for a list of available commands.")

    def help(self):
        print("Available commands:")
        print("ls - List files and folders in the current directory")
        print("pwd - Print the current working directory")
        print("cd <folder> - Change directory to the specified folder")
        print("cat <file> - View the content of a file")
        print("mkdir <folder> - Create a new folder")
        print("touch <file> - Create a new file")
        print("rm <file> - Delete a file")
        print("rmdir <folder> - Delete an empty folder")
        print("write <file> <content> - Write content to a file")
        print("cp <source_file> <destination_file> - Copy a file to a new location")
        print("mv <source_file> <destination_file> - Move/rename a file to a new location")
        print("size <file/folder> - Get the size of a file or folder")
        print("chmod <file> <permissions> - Change the permissions of a file")
        print("journaling - Save a log of actions to a journal file")
        print("help - Display this help message")
        print("exit - Exit the file system")

    def ls(self):
        for item in self.current_folder.contents:
            if isinstance(item, File):
                created_time = item.format_timestamp()
                permissions = item.get_permissions()
                print(f"{permissions} {item.name} [Created: {created_time}]")
        for item in self.current_folder.contents:
            if isinstance(item, Folder):
                created_time = item.format_timestamp()
                print(f"{item.name}/ [Created: {created_time}]")

    def pwd(self):
        path = self.get_full_path(self.current_folder)
        print(f"Current directory: {path}")

    def get_full_path(self, folder):
        if folder == self.root:
            return "/" + folder.name
        parent_path = self.get_full_path(folder.parent)
        return os.path.join(parent_path, folder.name)

    def cd(self, folder_name):
        if folder_name == "..":
            if self.current_folder != self.root:
                self.current_folder = self.current_folder.parent
        else:
            for item in self.current_folder.contents:
                if isinstance(item, Folder) and item.name == folder_name:
                    self.current_folder = item
                    break
            else:
                print(f"Folder '{folder_name}' not found.")
        self.journal.append(f"Changed directory to '{self.current_folder.name}'")

    def cat(self, file_name):
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == file_name:
                print(item.content)
                return
        print(f"File '{file_name}' not found.")

    def mkdir(self, folder_name):
        for item in self.current_folder.contents:
            if isinstance(item, Folder) and item.name == folder_name:
                print(f"Folder '{folder_name}' already exists.")
                return
        new_folder = Folder(folder_name)
        new_folder.parent = self.current_folder  # Set parent
        self.current_folder.contents.append(new_folder)
        self.journal.append(f"Created folder '{folder_name}' at {new_folder.created_time}")

    def touch(self, file_name):
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == file_name:
                print(f"File '{file_name}' already exists.")
                return
        new_file = File(file_name)
        new_file.parent = self.current_folder  # Set parent
        self.current_folder.contents.append(new_file)
        self.journal.append(f"Created file '{file_name}' at {new_file.created_time}")

    def rm(self, file_name):
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == file_name:
                self.current_folder.contents.remove(item)
                self.journal.append(f"Deleted file '{file_name}'")
                return
        print(f"File '{file_name}' not found.")

    def rmdir(self, folder_name):
        for item in self.current_folder.contents:
            if isinstance(item, Folder) and item.name == folder_name:
                self.current_folder.contents.remove(item)
                self.journal.append(f"Deleted folder '{folder_name}'")
                return
        print(f"Folder '{folder_name}' not found.")

    def write(self, file_name, content):
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == file_name:
                item.write(content)
                self.journal.append(f"Modified file '{file_name}' at {item.modified_time}")
                return

        new_file = File(file_name, content)
        new_file.parent = self.current_folder  # Set parent
        self.current_folder.contents.append(new_file)
        self.journal.append(f"Created file '{file_name}' at {new_file.created_time}")

    def cp(self, source_file, destination_file):
        source = None
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == source_file:
                source = item
                break
        if not source:
            print(f"Source file '{source_file}' not found.")
            return
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == destination_file:
                print(f"Destination file '{destination_file}' already exists.")
                return
        destination = File(destination_file, source.content, source.permissions)
        destination.parent = self.current_folder  # Set parent
        self.current_folder.contents.append(destination)
        self.journal.append(f"Copied file '{source_file}' to '{destination_file}' at {destination.created_time}")

    def mv(self, source_file, destination_file):
        source = None
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == source_file:
                source = item
                break
        if not source:
            print(f"Source file '{source_file}' not found.")
            return
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == destination_file:
                print(f"Destination file '{destination_file}' already exists.")
                return
        source.name = destination_file
        source.modified_time = datetime.now()  # Update modified time
        self.journal.append(f"Moved file '{source_file}' to '{destination_file}' at {source.modified_time}")

    def size(self, name):
        for item in self.current_folder.contents:
            if item.name == name:
                if isinstance(item, File):
                    print(f"Size of '{name}': {item.get_size()} bytes")
                elif isinstance(item, Folder):
                    print(f"Size of '{name}': {item.get_size()} bytes")
                return
        print(f"File or folder '{name}' not found.")

    def chmod(self, file_name, permissions):
        for item in self.current_folder.contents:
            if isinstance(item, File) and item.name == file_name:
                old_permissions = item.get_permissions()
                item.chmod(permissions)
                self.journal.append(f"Changed permissions of '{file_name}' from {old_permissions} to '{permissions}'")
                return
        print(f"File '{file_name}' not found.")

    def journaling(self):
        with open("journal.txt", "w") as journal_file:
            for entry in self.journal:
                journal_file.write(entry + "\n")

def embed():
    fs = FileSystem()
    fs.run()
    fs.journaling()

if __name__ == "__main__":
    embed()
