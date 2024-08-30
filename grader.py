"""
Grader class that grades students with matlab tests or python tests.
"""

import os
import zipfile
from pathlib import Path
import shutil
import subprocess


def execute_system_call(command):
    """
    Execute a system call and return the output
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    return result.stdout


class Grader():
    """
    Grader class that grades students with matlab tests or python tests.
    """
    def __init__(self, submission_file, submission_dir, test_dir):
        self.submission_file = submission_file
        self.submission_dir = submission_dir
        self.test_dir = test_dir


        for file in os.listdir(test_dir):
            if file.endswith('.m'):
                self.matlab_test = file
                print(f"MATLAB test {self.matlab_test} found!\n\n")
            elif file.endswith('.py'):
                self.python_test = file
                print(f"PYTHON test {self.python_test} found!\n\n")

        print('==============  Grader initialized! =============\n\n')


    def unzip(self, file, file_dir):
        """
        Unzip the submission file
        """
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(file_dir)


    def grade(self, hw_str='hw00'):
        """
        Grade the students

        @param hw_str: The homework string
        """
        # create a file to store the grades
        grades_file = open(hw_str + '.csv', 'w', encoding='utf-8')

        # Unzip the submission file
        if not os.path.exists(self.submission_dir):
            print('Unzipping the submission file ...')
            self.unzip(self.submission_file, self.submission_dir)

        # Get the student's directory
        total_students = 0
        student_dirs = []
        for student in os.listdir(self.submission_dir):
            student_dir = os.path.join(self.submission_dir, student)
            if student_dir.endswith('.zip'):
                student_dirs.append(student_dir)
                total_students += 1

        for i in range(total_students):

            student_file = student_dirs[i]
            student_dir = os.path.join(self.submission_dir, Path(student_file).stem)
            self.unzip(student_file, student_dir)

            if os.path.exists(os.path.join(student_dir, hw_str + '.m')):
                student_code = 'matlab'
                code_file = open(os.path.join(student_dir, hw_str + '.m'), 'r', encoding='utf-8')
                # get author information
                email = code_file.readlines()[0].split('%')[1]\
                    .replace('Author:', '').replace('/', ' ').strip().split(' ')[-1]
                code_file.close()
                # copy the test file to the student's directory
                shutil.copy(os.path.join(self.test_dir, self.matlab_test), student_dir)
                # run the test file
                student_score = execute_system_call(\
                        f'matlab -nojvm -nosplash -nodesktop -batch \
                        "run(\'{os.path.join(student_dir, self.matlab_test)}\');exit;"')

                cnt_passes = student_score.count('PASS')

                print(f'Student {(i+1): 3d}/{total_students: 3d} scored: {cnt_passes} | {student_dir} \n')

                grades_file.write(f'{Path(student_file).stem[0:26]}, {email}, {student_code}, {cnt_passes}\n')

            elif os.path.exists(os.path.join(student_dir, hw_str + '.py')):
                # print('Python file found!')
                student_code = 'python'
                code_file = open(os.path.join(student_dir, hw_str + '.py'), 'r', encoding='utf-8')
                # get author information
                email = code_file.readlines()[0].split('#')[1]\
                    .replace('Author:', '').replace('/', ' ').strip().split(' ')[-1]
                code_file.close()
                # copy the test file to the student's directory
                shutil.copy(os.path.join(self.test_dir, self.python_test), student_dir)
                # run the test file
                student_score = execute_system_call(\
                        f'python {os.path.join(student_dir, self.python_test)}')
                
                cnt_passes = student_score.count('PASS')
                print(f'Student {(i+1): 3d}/{total_students: 3d} scored: {cnt_passes} | {student_dir} \n')

                grades_file.write(f'{Path(student_file).stem[0:26]}, {email}, {student_code}, {cnt_passes}\n')

            else:
                student_code = 'other'
                grades_file.write(f'{Path(student_file).stem[0:26]}, , ,\n')

        grades_file.close()
