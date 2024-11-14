import tarfile
import io
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch
from main import *

class TestShellCommands(unittest.TestCase):

    def setUp(self):
        # Мокируем tar-файл
        self.tar = tarfile.open('root.tar', 'r')
        self.log_file_path = 'log.xml'
        self.mock_log_file = ET.Element("session")

    def tearDown(self):
        self.tar.close()

    def test_cd_root(self):
        current_path = "/root"
        new_path = change_directory(current_path, "/", self.tar, self.mock_log_file)
        self.assertEqual(new_path, "/root")

    def test_cd_to_projectB(self):
        current_path = "/root/home/user/documents"
        new_path = change_directory(current_path, "projects/projectB", self.tar, self.mock_log_file)
        self.assertEqual(new_path, "/root/home/user/documents/projects/projectB")

    def test_cd_to_parent_directory(self):
        current_path = "/root/home/user/documents/projects/projectA"
        new_path = change_directory(current_path, "..", self.tar, self.mock_log_file)
        self.assertEqual(new_path, "/root/home/user/documents/projects")

    def test_ls_in_documents(self):
        current_path = "/root/home/user/documents"
        with io.StringIO() as buf, redirect_stdout(buf):
            list_directory(current_path, self.tar, self.mock_log_file)
            output = buf.getvalue().strip().split('\n')
        expected_output = ['downloads', 'images', 'notes', 'projects', 'reports']
        self.assertEqual(sorted(output), sorted(expected_output))

    def test_ls_in_projectA(self):
        current_path = "/root/home/user/documents/projects/projectA"
        with io.StringIO() as buf, redirect_stdout(buf):
            list_directory(current_path, self.tar, self.mock_log_file)
            output = buf.getvalue().strip().split('\n')
        expected_output = ['src']
        self.assertEqual(sorted(output), sorted(expected_output))

    def test_ls_in_empty_directory(self):
        current_path = "/root/home/user/empty_folder"
        with io.StringIO() as buf, redirect_stdout(buf):
            list_directory(current_path, self.tar, self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertEqual(output, "")

    def test_tree(self):
        current_path = "/root/home/user/documents"
        with io.StringIO() as buf, redirect_stdout(buf):
            tree(current_path, self.tar.getnames(), self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertIn('projects/', output)
        self.assertIn('report.pdf', output)

    def test_tree_in_projectA(self):
        current_path = "/root/home/user/documents/projects/projectA"
        with io.StringIO() as buf, redirect_stdout(buf):
            tree(current_path, self.tar.getnames(), self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertIn('src/', output)

    def test_tree_empty_directory(self):
        current_path = "/root/home/user/empty_folder"
        with io.StringIO() as buf, redirect_stdout(buf):
            tree(current_path, self.tar.getnames(), self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertEqual(output, "")

    def test_du(self):
        current_path = "/root/home/user/documents"
        with io.StringIO() as buf, redirect_stdout(buf):
            du(current_path, self.tar, self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertIn('bytes', output)  # Проверка на вывод размера

    def test_find_valid_file(self):
        current_path = "/root/home/user/documents"
        with io.StringIO() as buf, redirect_stdout(buf):
            find(current_path, 'notes', self.tar, self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertIn('notes', output)

    def test_find_nonexistent_file(self):
        current_path = "/root/home/user/documents"
        with io.StringIO() as buf, redirect_stdout(buf):
            find(current_path, 'nonexistent', self.tar, self.mock_log_file)
            output = buf.getvalue().strip()
        self.assertIn('find: nonexistent not found', output)

    def test_exit(self):
        # Мы будем проверять, что при выходе вызывается правильная логика
        with self.assertRaises(SystemExit):
            exit_shell(self.mock_log_file, self.log_file_path)

    def test_log_action(self):
        # Проверяем, что логируются действия
        log_action(self.mock_log_file, "cd", "Changed directory to /root/home/user")
        self.assertEqual(len(self.mock_log_file), 1)
        self.assertEqual(self.mock_log_file[0].tag, 'action')
        self.assertEqual(self.mock_log_file[0].attrib['command'], 'cd')
        self.assertEqual(self.mock_log_file[0].text, 'Changed directory to /root/home/user')

    def test_save_log(self):
        # Проверяем, что лог сохраняется
        save_log(self.log_file_path, self.mock_log_file)
        with open(self.log_file_path, 'r') as f:
            content = f.read()
        self.assertIn('<session>', content)


if __name__ == '__main__':
    unittest.main()
