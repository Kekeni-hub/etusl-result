# Generated migration for GPA and total score fields in StudentSemesterFolder

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_studentsemesterfolder_result_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentsemesterfolder',
            name='total_score',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='studentsemesterfolder',
            name='gpa',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name='studentsemesterfolder',
            name='is_gpa_calculated',
            field=models.BooleanField(default=False),
        ),
    ]
