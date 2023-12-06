import random
from collections import defaultdict
from itertools import product, chain

class Student():
    def __init__(self, student_id, n_courses, year = 0, department = None, credit_limit = 4):
        self.year = year
        self.dept = department
        self.n_courses = n_courses
        self.credit_limit = credit_limit
        self.student_id = student_id
        
        self._generate_preferences() # indices in the course_list
        
        self.eligible = True
        self.course_enroll = [] # indices in the course_list
        self.current_course_propose = 0 # index in the course_prefs
        
        
    def __str__(self):
        return f"y{self.year}d{self.dept:02d}s{self.student_id:04d}"
    
    def __repr__(self):
        return f"y{self.year}d{self.dept:02d}s{self.student_id:04d}"
        
    def _generate_preferences(self):
        self.course_prefs = list(range(self.n_courses))
        random.shuffle(self.course_prefs) # randomly shuffle course preferences
        
    def update_current_course_prefs(self, index):
        self.current_course_propose = index
        if self.current_course_propose >= self.n_courses:
            self.eligible = False
    
    def make_proposals(self):
        # if enroll less than the limit and still has a course that can propose to
        if (len(self.course_enroll) < self.credit_limit) and self.eligible:
            start = self.current_course_propose
            end = min(self.current_course_propose + (self.credit_limit - len(self.course_enroll)),
                      self.n_courses)
            course_indices = self.course_prefs[start: end]
            self.update_current_course_prefs(end)
            return course_indices
        return []
            
    def add_course(self, course_id):
        if course_id not in self.course_enroll:
            self.course_enroll.append(course_id)
        
    def remove_course(self, course_id):
        if course_id in self.course_enroll:
            self.course_enroll.remove(course_id)
            
    def get_utilities(self):
        util = sum([self.n_courses - self.course_prefs.index(c) for c in self.course_enroll])
        return util
    
    def get_utilities_from_courses(self, courses):
        util = sum([self.n_courses - self.course_prefs.index(c) for c in courses])
        return util

    def get_enrollment_info(self):
        output = f"Student {self.__str__()} enrolls in {len(self.course_enroll)} courses: {self.course_enroll}\n"
        output += f"\twith utility {self.get_utilities()}"
        print(output)

    def determine_conflicts(self, course_list):
        # Check if there are conflicting courses
        enroll_course_schedules = defaultdict(list) # time: c_list
        for c in self.course_enroll:
            enroll_course_schedules[course_list[c].time].append(c)
        conflict_courses = {t: c_list for t, c_list in enroll_course_schedules.items() if len(c_list) > 1}
        nonconflict_courses = [c for c in self.course_enroll if c not in list(chain(*conflict_courses.values()))]
        
        # keep non-conflicting most-preferred courses (providing the highest total utility)
        self.unavailable_times = enroll_course_schedules.keys()
        max_util = -1
        to_keep_courses = []
        for comb in product(*conflict_courses.values()):
            util = self.get_utilities_from_courses(nonconflict_courses) + self.get_utilities_from_courses(list(comb))
            if util > max_util:
                max_util = util
                to_keep_courses = list(comb)

        # update courses to keep enrollment
        old_courses = self.course_enroll.copy()
        self.course_enroll = nonconflict_courses + to_keep_courses
        for c in old_courses:
            if c not in self.course_enroll:
                course_list[c].drop_student(self)

        self.eligible = True
        self.current_course_propose = 0  # index in the course_prefs
    
    def make_resolving_proposals(self, course_list):
        # if enroll less than the limit and still has a course that can propose to
        course_indices = []
        while (len(course_indices) + len(self.course_enroll) < self.credit_limit) and self.eligible:
            c_index = self.current_course_propose
            if course_list[c_index].time not in self.unavailable_times: # no conflict
                course_indices.append(c_index)
            self.update_current_course_prefs(c_index + 1)
        return course_indices
        
# =============================================================================== # 

class Course():
    def __init__(self, course_id, student_list, department = None, enroll_limit = 80):
        self.dept = department
        self.course_id = course_id
        self.enroll_limit = enroll_limit
        
        self._generate_preferences(student_list)
        self.student_enroll = []
        self.second_student_enroll = []

        self.time = None
        
    def __str__(self):
        return f"d{self.dept:02d}c{self.course_id:04d}"
    
    def __repr__(self):
        return f"d{self.dept:02d}c{self.course_id:04d}"
    
    def drop_student(self, student):
        if student in self.student_enroll:
            self.student_enroll.remove(student)
    
    def set_enroll_limit(self, new_limit):
        self.enroll_limit = new_limit

    def set_time(self, time):
        self.time = time
        
    def _generate_preferences(self, student_list):
        self.student_prefs = []
        # add students from its own department first (ranked in decreasing order of class year)
        # break ties randomly
        same_dept_students = [student for student in student_list if student.dept == self.dept]
        for year in range(3, -1, -1):
            same_dept_year = [student for student in same_dept_students if student.year == year]
            random.shuffle(same_dept_year)
            self.student_prefs += same_dept_year
        
        # then students from other depts (ranked in decreasing order of class year)
        other_dept_students = [student for student in student_list if student.dept != self.dept]
        # self.student_prefs += sorted(other_dept_students, key = lambda x: x.year, reverse = True)
        for year in range(3, -1, -1):
            other_dept_year = [student for student in other_dept_students if student.year == year]
            random.shuffle(other_dept_year)
            self.student_prefs += other_dept_year
            
        self.student_prefs_dict = {student.student_id: index 
                                   for index, student in enumerate(self.student_prefs)}
        
    def accept_proposals(self, proposals):
        # tentatively accept and returns whether accept or reject (return accepts, rejects tuple)
        if (len(self.student_enroll) + len(proposals)) <= self.enroll_limit:
            # tentatively accept all
            self.student_enroll += proposals
            return proposals, []
        else:
            # find the most preferred students
            combined = self.student_enroll + proposals
            combined = sorted(combined, key = lambda student: self.student_prefs_dict[student.student_id])
            accepts = combined[: self.enroll_limit]
            rejects = combined[self.enroll_limit: ]
            self.student_enroll = accepts
            return accepts, rejects

    def accept_resolving_proposals(self, proposals):
        # tentatively accept and returns whether accept or reject (return accepts, rejects tuple)
        if (len(self.student_enroll) + len(self.second_student_enroll) + len(proposals)) <= self.enroll_limit:
            # tentatively accept all
            self.second_student_enroll += proposals
            return proposals, []
        else:
            # find the most preferred students
            combined = self.second_student_enroll + proposals
            combined = sorted(combined, key = lambda student: self.student_prefs_dict[student.student_id])
            accepts = combined[: self.enroll_limit - len(self.student_enroll)]
            rejects = combined[self.enroll_limit - len(self.student_enroll): ]
            self.second_student_enroll = accepts
            return accepts, rejects
        
    def finalize_enrollment(self):
        self.student_enroll = self.student_enroll + self.second_student_enroll
        
    def get_enrollment_info(self):
        output = f"Course {self.__str__()} has {len(self.student_enroll)} students enrolling"
        print(output)