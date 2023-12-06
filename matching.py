from collections import defaultdict

from agent import Student, Course


def find_matching(student_list, course_list):
    da_round = 0
    
    while True:
        da_round += 1
        print(f"Round: {da_round}")
        # proposals = dict course_list_index: students
        proposals = defaultdict(list)
        
        n_proposals = 0 # check if no proposals can be made, terminate
        
        # students propose to courses
        for s in student_list:
            class_to_propose = s.make_proposals()
            for c in class_to_propose: 
                proposals[c].append(s)
                n_proposals += 1
            
        if n_proposals == 0: # check if no proposals can be made, terminate
            # finalize enrollment
            print("\tDA terminates and all proposals have been finalized.")
            break
        
        print(f"\tNumber of proposals made: {n_proposals}")
        
        n_rejects = 0
        # otherwise, courses tentatively accept proposing students based on their preferences
        for course_id, student_proposals in proposals.items():
            accepts, rejects = course_list[course_id].accept_proposals(student_proposals)
            for student in accepts:
                student.add_course(course_id)
            for student in rejects:
                student.remove_course(course_id)
                n_rejects += 1
        print(f"\tNumber of proposals being rejected: {n_rejects}")
    
    
    return student_list, course_list

# =============================================================================== # 

def resolve_conflicts(student_list, course_list):
    da_round = 0
    
    while True:
        da_round += 1
        print(f"Round: {da_round}")
        # proposals = dict course_list_index: students
        proposals = defaultdict(list)
        
        n_proposals = 0 # check if no proposals can be made, terminate
        
        # students propose to courses
        for s in student_list:
            class_to_propose = s.make_resolving_proposals(course_list)
            for c in class_to_propose: 
                proposals[c].append(s)
                n_proposals += 1
            
        if n_proposals == 0: # check if no proposals can be made, terminate
            # finalize enrollment
            print("\tDA terminates and all proposals have been finalized.")
            for c in course_list:
                c.finalize_enrollment()
            break
        
        print(f"\tNumber of proposals made: {n_proposals}")
        
        n_rejects = 0
        # otherwise, courses tentatively accept proposing students based on their preferences
        for course_id, student_proposals in proposals.items():
            accepts, rejects = course_list[course_id].accept_resolving_proposals(student_proposals)
            for student in accepts:
                student.add_course(course_id)
            for student in rejects:
                student.remove_course(course_id)
                n_rejects += 1
        print(f"\tNumber of proposals being rejected: {n_rejects}")
    return student_list, course_list
