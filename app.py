
from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

df = pd.read_excel('data.xlsx', dtype={'roll': str, 'phone': str})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student', methods=['POST'])
def get_student_info():
    roll_number = request.form['roll_number']
    student_data = df[df['roll'] == roll_number]
    if not student_data.empty:
        student = student_data.iloc[0].to_dict()

        # Remove keys with NaN values
        student = {k: v for k, v in student.items() if pd.notna(v)}

        return render_template('student_info.html', student=student)
    return render_template('student_info.html', error="Student not found")

@app.route('/section', methods=['POST'])
def get_section_info():
    branch = request.form['branch']#+
    section = request.form['section']
    year = request.form.get('year')  # Get the year from the form

    # Determine the correct column based on the year
    if year == '2':
        section_column = 'sec2nd'
    elif year == '3':
        section_column = 'section-6th'
    else:
        return render_template('section_info.html', error="Invalid year selected")

    # Construct the full section name#+
    full_section = f"{branch}-{section.zfill(2)}"#+
    # Filter the DataFrame based on the selected section and year

    section_data = df[df[section_column].str.contains(full_section, na=False)]#+
    if not section_data.empty:
        total_students = len(section_data)
        male_students = section_data['hostel'].str.startswith('KP').sum()
        female_students = section_data['hostel'].str.startswith('QC').sum()
        day_scholars = total_students - male_students - female_students
        return render_template('section_info.html', 
                               total=total_students, 
                               male=male_students, 
                               female=female_students, 
                               day_scholars=day_scholars,
                               students=section_data.to_dict('records'))
    return render_template('section_info.html', error="Section not found")

if __name__ == '__main__':
    app.run(debug=True)
