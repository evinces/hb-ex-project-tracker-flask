"""A web application for tracking projects, students, and student grades."""

from flask import Flask, request, render_template, flash, redirect

import hackbright

app = Flask(__name__)
app.secret_key = "SOME REALLY SECRET KEY (shhhhh)"


@app.route("/")
def index():
    """Display homepage"""

    students = hackbright.get_all_students()
    projects = [project[0] for project in hackbright.get_all_projects()]

    return render_template("index.html", students=students, projects=projects)


# Students


@app.route("/student-search")
def get_student_form():
    """Display student search form"""

    return render_template("student_search.html")


@app.route("/student")
def get_student():
    """Show information about a student."""

    github = request.args.get('github')

    first, last, github = hackbright.get_student_by_github(github)

    grades = hackbright.get_grades_by_github(github)

    return render_template("student_info.html", github=github, first=first,
                           last=last, grades=grades)


@app.route("/student-add", methods=['POST'])
def add_student():
    """Add a new student"""

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    github = request.form.get("github")

    hackbright.make_new_student(first_name, last_name, github)

    flash(('student', github))

    return redirect("/student-add")


@app.route("/student-add", methods=['GET'])
def get_add_student_form():
    """Display new student form"""

    return render_template("new_student_form.html")


# Projects


@app.route("/project-add", methods=['POST'])
def add_project():
    """Add a new project"""

    title = request.form.get("title")
    desc = request.form.get("desc")
    max_grade = request.form.get("max_grade")

    hackbright.make_new_project(title, desc, max_grade)

    flash(('project', title))

    return redirect("/project-add")


@app.route("/project-add", methods=['GET'])
def get_add_project_form():
    """Display new project form"""

    return render_template("new_project_form.html")


@app.route("/project")
def get_project_info():
    """Display project info"""

    title = request.args.get("title")

    _, desc, max_grade = hackbright.get_project_by_title(title)

    grades = hackbright.get_grades_by_title(title)

    names = {}

    for github, _ in grades:
        first_name, last_name, _ = hackbright.get_student_by_github(github)
        names[github] = "{first} {last}".format(first=first_name,
                                                last=last_name)

    return render_template("project_info.html", title=title, desc=desc,
                           max_grade=max_grade, grades=grades, names=names)


# Grades

@app.route("/grade-add", methods=['POST'])
def add_grade():
    """Add a new grade"""

    project_title = request.form.get("project_title")
    student_github = request.form.get("student_github")
    grade = request.form.get("grade")

    if hackbright.get_grade_by_github_title(student_github, project_title) is None:
        hackbright.assign_grade(student_github, project_title, grade)
    else:
        hackbright.update_grade(student_github, project_title, grade)

    flash(('grade', project_title))

    return redirect("/grade-add")


@app.route("/grade-add", methods=['GET'])
def get_add_grade_form():
    """Display new grade form"""

    students = hackbright.get_all_students()
    projects = [project[0] for project in hackbright.get_all_projects()]

    return render_template("new_grade_form.html", students=students,
                           projects=projects)


if __name__ == "__main__":
    hackbright.connect_to_db(app)
    app.run(debug=True)
