import random
from collections import defaultdict
from itertools import combinations, product, chain

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import networkx as nx

import argparse

from agent import Student, Course
from matching import *
from simulate import * 


def main(n_students = 5000, n_courses = 100, n_depts = 15, 
        credit_limit = 4, enroll_limit = 80, n_slots = 12):

    student_list, course_list = generate_data(n_students = n_students, 
                                            n_courses = n_courses, 
                                            n_depts = n_depts, 
                                            credit_limit = credit_limit,
                                            enroll_limit = enroll_limit)

    student_list, course_list = find_matching(student_list, course_list)

    student_utilities = [s.get_utilities() for s in student_list]
    
    plt.clf()
    sns.histplot(student_utilities, stat = 'percent', color = 'seagreen')
    plt.xlabel("Student utiltities")
    filename = f"results/fig/utils_match_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)

    course_enroll_sizes = [len(c.student_enroll) for c in course_list]
    plt.clf()
    sns.histplot(course_enroll_sizes, stat = 'percent', color = 'seagreen')
    plt.xlabel("Course sizes")
    filename = f"results/fig/csizes_match_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)

    # Sanity checks
    for c in course_list:
        for s in c.student_enroll:
            assert c.course_id in s.course_enroll
            
        assert len(c.student_enroll) <= c.enroll_limit

    for s in student_list:
        assert len(s.course_enroll) <= s.credit_limit


    # Course scheduling
    conflict_counts = defaultdict(int)

    for s in student_list:
        for c1, c2 in combinations(sorted(s.course_enroll), 2):
            conflict_counts[(c1, c2)] += 1

    print(f"number of edges: {len(conflict_counts)}")
    print(f"total number of conflicts: {sum(conflict_counts.values())}")

    graph = nx.Graph()
    graph.add_weighted_edges_from([(c[0], c[1], n * (-1) + max(conflict_counts.values())) 
                                for c, n in conflict_counts.items()])
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")

    T = nx.gomory_hu_tree(graph, capacity = 'weight')
    min_weight_k_edges = sorted([e for e in T.edges(data = True)], 
                                key = lambda x: x[2]['weight'],
                                reverse = False)[: n_slots - 1]
    for node1, node2, data in min_weight_k_edges:
        print(f"({node1}, {node2}) with weight {data['weight']}")

    T.remove_edges_from(min_weight_k_edges)
    components = list(nx.connected_components(T))
    print(f"Number of components: {len(components)}")
    for i, comp in enumerate(components):
        print(f"Component {i}: size = {len(comp)} -> {list(comp)}")

    # Assign time to courses and resolve conflicts among students
    for t, c_list in enumerate(components):
        for c in list(c_list):
            course_list[c].set_time(t)

    for s in student_list:
        s.determine_conflicts(course_list)

    student_list, course_list = resolve_conflicts(student_list, course_list)

    # sanity checks
    for c in course_list:
        for s in c.student_enroll:
            assert c.course_id in s.course_enroll
            
        assert len(c.student_enroll) <= c.enroll_limit

    for s in student_list:
        assert len(s.course_enroll) <= s.credit_limit


    student_utilities = [s.get_utilities() for s in student_list]
    total_welfare = sum(student_utilities)
    plt.clf()
    sns.histplot(student_utilities, stat = 'percent', color = 'seagreen')
    plt.xlabel("Student utiltities")
    filename = f"results/fig/utils_resolve_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)

    course_enroll_sizes = [len(c.student_enroll) for c in course_list]
    plt.clf()
    sns.histplot(course_enroll_sizes, stat = 'percent', color = 'seagreen')
    plt.xlabel("Course sizes")
    filename = f"results/fig/csizes_resolve_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)


    # Run baseline
    student_list_baseline = [Student(s.student_id, s.n_courses, s.year, s.dept, s.credit_limit)
                            for s in student_list]
    # copy course prefs
    for s, s_baseline in zip(student_list, student_list_baseline):
        s_baseline.course_prefs = s.course_prefs.copy()
        

    course_list_baseline = [Course(c.course_id, [], c.dept, c.enroll_limit)
                            for c in course_list]
    # copy student prefs
    for c, c_baseline in zip(course_list, course_list_baseline):
        c_baseline.student_prefs = [student_list_baseline[s.student_id] for s in c.student_prefs]
        c_baseline.student_prefs_dict = {student.student_id: index 
                                    for index, student in enumerate(c_baseline.student_prefs)}
        
    # Randomly assign times for courses
    for c_baseline in course_list_baseline:
        c_baseline.set_time(np.random.randint(n_slots))
        
    student_list_baseline, course_list_baseline = resolve_conflicts(student_list_baseline, course_list_baseline)


    student_utilities_baseline = [s.get_utilities() for s in student_list_baseline]
    total_welfare_baseline = sum(student_utilities_baseline)
    plt.clf()
    sns.histplot(student_utilities_baseline, stat = 'percent', color = 'seagreen')
    plt.xlabel("Student utiltities")
    filename = f"results/fig/utils_baseline_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)

    course_enroll_sizes_baseline = [len(c.student_enroll) for c in course_list_baseline]
    plt.clf()
    sns.histplot(course_enroll_sizes_baseline, stat = 'percent', color = 'seagreen')
    plt.xlabel("Course sizes")
    filename = f"results/fig/csizes_baseline_s{n_students}c{n_courses}d{n_depts}cl{credit_limit}el{enroll_limit}k{n_slots}"
    plt.savefig(filename)

    print(f"\n\nParameters:")
    print(f"\ts={n_students}, c={n_courses}, d={n_depts}, cl={credit_limit}, el={enroll_limit}, k={n_slots}")
    print(f"Average welfare:")
    print(f"\tproposed method: {1.0 * total_welfare / n_students : .2f}")
    print(f"\tbaseline: {1.0 * total_welfare_baseline / n_students : .2f}")
    print(f"\twelfare gain: {1.0 * (total_welfare - total_welfare_baseline) / n_students : .2f}\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('--n_students', type = int, default = 5000,
                    help='Number of students')
    parser.add_argument('--n_courses', type = int, default = 100,
                    help='Number of courses')
    parser.add_argument('--n_depts', type = int, default = 15,
                    help='Number of departments')
    parser.add_argument('--credit_limit', type = int, default = 4,
                    help='Credit limit for each student')
    parser.add_argument('--enroll_limit', type = int, default = 80,
                    help='Enroll limit for each student')
    parser.add_argument('--n_slots', type = int, default = 12,
                    help='Number of time slots available')
    
    args = parser.parse_args()
    main(n_students = args.n_students, n_courses = args.n_courses,
        n_depts = args.n_depts, credit_limit = args.credit_limit,
        enroll_limit = args.enroll_limit, n_slots = args.n_slots)
