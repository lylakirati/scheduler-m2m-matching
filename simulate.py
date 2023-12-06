from collections import defaultdict
from itertools import combinations, product, chain

import numpy as np

from agent import Student, Course

def generate_data(n_students = 5000, n_courses = 100, n_depts = 15, credit_limit = 4, enroll_limit = 80):
    student_list = []
    course_list = []

    n_years = 4
    for i in range(n_students):
        student_list.append(Student(
            student_id = i,
            n_courses = n_courses,
            year = np.random.randint(n_years),
            department = np.random.randint(n_depts),
            credit_limit = credit_limit
        ))
        
    for i in range(n_courses):
        course_list.append(Course(
            course_id = i,
            student_list = student_list,
            department = np.random.randint(n_depts),
            enroll_limit = enroll_limit
        ))
    return student_list, course_list