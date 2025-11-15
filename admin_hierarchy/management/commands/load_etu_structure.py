from django.core.management.base import BaseCommand
from admin_hierarchy.models import *
from student.models import Faculty, Department, Program

class Command(BaseCommand):
    help = 'Load Eastern Technical University (ETUSL) faculties, departments and programs'

    def handle(self, *args, **options):
        created = 0

        # Faculty of Engineering & Innovation
        f_eng, _ = Faculty.objects.get_or_create(name='Faculty of Engineering & Innovation', code='FEI')
        eng_depts = [
            ('Civil and Environmental Engineering', 'CEE'),
            ('Electrical & Electronics Engineering', 'EEE'),
            ('Mechanical & Manufacturing Engineering', 'MME'),
            ('Mining Engineering', 'MIN'),
            ('Agricultural Engineering', 'AGE'),
        ]
        eng_programs = [
            ('Renewable Energy', 'B.Eng. Renewable Energy'),
            ('Building Construction', 'B.Eng. Building Construction'),
            ('Information Systems Management', 'B.Eng. Information Systems Management'),
        ]
        for name, code in eng_depts:
            d, _ = Department.objects.get_or_create(name=name, code=code, faculty=f_eng)
        for pname, pcode in eng_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_eng).first())

        # Faculty of Vocational & Skills Development Studies
        f_voc, _ = Faculty.objects.get_or_create(name='Faculty of Vocational & Skills Development Studies', code='FVSD')
        voc_depts = [
            ('Plumbing', 'PLB'),
            ('Wood Product Processing', 'WPP'),
            ('Fashion & Design', 'FAD'),
        ]
        voc_programs = [
            ('Masonry', 'Masonry Diploma'),
            ('Plumbing & Pipe-Fitting', 'Plumbing Diploma'),
            ('Land Surveying', 'Surveying Diploma'),
            ('Electrical Technology', 'Electrical Diploma'),
            ('Carpentry', 'Carpentry Diploma'),
            ('Welding', 'Welding Diploma'),
            ('Catering', 'Catering Diploma'),
        ]
        for name, code in voc_depts:
            Department.objects.get_or_create(name=name, code=code, faculty=f_voc)
        for pname, pcode in voc_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_voc).first())

        # Faculty of Pure & Applied Sciences
        f_sci, _ = Faculty.objects.get_or_create(name='Faculty of Pure & Applied Sciences', code='FPAS')
        sci_depts = [
            ('Physics', 'PHY'),
            ('Chemistry', 'CHE'),
            ('Mathematics and Statistics', 'MST'),
            ('Biological Sciences', 'BIO'),
            ('Environmental Science and Geography', 'ENV'),
        ]
        sci_programs = [
            ('Environmental Science', 'BSc Environmental Science'),
            ('Physics', 'BSc Physics'),
            ('Mathematics', 'BSc Mathematics'),
            ('Chemistry', 'BSc Chemistry'),
            ('Biology', 'BSc Biology'),
        ]
        for name, code in sci_depts:
            Department.objects.get_or_create(name=name, code=code, faculty=f_sci)
        for pname, pcode in sci_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_sci).first())

        # Faculty of Health Sciences & Disaster Management
        f_health, _ = Faculty.objects.get_or_create(name='Faculty of Health Sciences & Disaster Management', code='FHSD')
        health_depts = [
            ('Nursing', 'NUR'),
            ('Public Health', 'PH'),
            ('Health Information Management', 'HIM'),
        ]
        health_programs = [
            ('Nursing', 'BSc Nursing'),
            ('Public Health', 'BSc Public Health'),
            ('Behavioural and Health Education', 'BSc Behavioural Health'),
        ]
        for name, code in health_depts:
            Department.objects.get_or_create(name=name, code=code, faculty=f_health)
        for pname, pcode in health_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_health).first())

        # Faculty of Development Agriculture & Natural Resources Management
        f_agri, _ = Faculty.objects.get_or_create(name='Faculty of Development Agriculture & Natural Resources Management', code='FDANR')
        agri_depts = [
            ('Agronomy', 'AGR'),
            ('Animal Science', 'ANS'),
            ('Agricultural Economics and Extension', 'AEE'),
            ('Fisheries and Aquaculture', 'FIA'),
        ]
        agri_programs = [
            ('Agriculture', 'BSc Agriculture'),
            ('Agribusiness', 'BSc Agribusiness'),
            ('Nutrition & Dietetics', 'BSc Nutrition'),
            ('Home Economics', 'BSc Home Economics'),
        ]
        for name, code in agri_depts:
            Department.objects.get_or_create(name=name, code=code, faculty=f_agri)
        for pname, pcode in agri_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_agri).first())

        # Faculty of Business & Entrepreneurship Studies
        f_bus, _ = Faculty.objects.get_or_create(name='Faculty of Business & Entrepreneurship Studies', code='FBES')
        bus_depts = [
            ('Accounting and Finance', 'ACF'),
            ('Business Administration', 'BAD'),
            ('Banking & Finance', 'BNF'),
            ('Entrepreneurship and Innovation', 'ENT'),
            ('Social Work and Peace Studies', 'SWP'),
        ]
        bus_programs = [
            ('Accounting', 'BSc Accounting'),
            ('Economics', 'BSc Economics'),
            ('Entrepreneurship', 'BSc Entrepreneurship'),
            ('Procurement', 'BSc Procurement'),
            ('Auditing', 'BSc Auditing'),
        ]
        for name, code in bus_depts:
            Department.objects.get_or_create(name=name, code=code, faculty=f_bus)
        for pname, pcode in bus_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_bus).first())

        # Faculty of Education
        f_edu, _ = Faculty.objects.get_or_create(name='Faculty of Education', code='FEDU')
        edu_depts = [
            ('Mathematics Education', 'MED'),
            ('Science Education', 'SED'),
            ('Home Economics Education', 'HED'),
            ('Agricultural Education', 'AGED'),
            ('Physical and Health Education', 'PHE'),
            ('English and Social Studies Education', 'ESSD'),
        ]
        edu_programs = [
            ('Education Administration', 'BEd Education Admin'),
            ('Guidance & Counselling', 'BEd Guidance Counselling'),
            ('Early Childhood Education', 'BEd Early Childhood'),
            ('Vocational Education', 'BEd Vocational Education'),
        ]
        edu_dept_objs = []
        for name, code in edu_depts:
            dept, _ = Department.objects.get_or_create(name=name, code=code, faculty=f_edu)
            edu_dept_objs.append(dept)
        for idx, (pname, pcode) in enumerate(edu_programs):
            dept = edu_dept_objs[idx % len(edu_dept_objs)]
            Program.objects.get_or_create(name=pname, code=pcode[:20], defaults={'department': dept})

        # Institute of Distance Education & CPD
        f_ide, _ = Faculty.objects.get_or_create(name='Institute of Distance Education & Continuous Professional Development', code='IDE')
        # Create a default department for IDE
        ide_dept, _ = Department.objects.get_or_create(name='Distance Education', code='IDE', faculty=f_ide)
        ide_programs = [
            ('Certificate in Agriculture', 'Cert Agriculture'),
            ('Certificate in Home Economics', 'Cert Home Economics'),
            ('Certificate in English', 'Cert English'),
            ('Certificate in Mathematics', 'Cert Math'),
            ('Certificate in Science', 'Cert Science'),
            ('Certificate in Library Science', 'Cert Library'),
            ('Certificate in Community Development', 'Cert Community'),
        ]
        for pname, pcode in ide_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], defaults={'department': ide_dept})

        # School of Postgraduate Studies
        f_pg, _ = Faculty.objects.get_or_create(name='School of Postgraduate Studies', code='SPGS')
        pg_depts = [
            ('Educational Management', 'EDM'),
            ('Disaster Management', 'DM'),
            ('Education', 'EDU'),
        ]
        pg_programs = [
            ('Postgraduate Diploma in Education', 'PGDE_PG'),
            ('Educational Administration', 'MSc_EDU_ADMIN'),
            ('Disaster Management', 'MSc_DISASTER'),
        ]
        pg_dept_objs = []
        for name, code in pg_depts:
            dept, _ = Department.objects.get_or_create(name=name, code=code, faculty=f_pg)
            pg_dept_objs.append(dept)
        for idx, (pname, pcode) in enumerate(pg_programs):
            dept = pg_dept_objs[idx % len(pg_dept_objs)]
            Program.objects.get_or_create(name=pname, code=pcode[:20], defaults={'department': dept})


        for pname, pcode in pg_programs:
            Program.objects.get_or_create(name=pname, code=pcode[:20], department=Department.objects.filter(faculty=f_pg).first())

        self.stdout.write(self.style.SUCCESS('ETU structure seeded successfully.'))
