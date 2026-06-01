from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_alter_blogpost_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='status',
            field=models.CharField(
                choices=[('draft', 'Draft'), ('published', 'Published')],
                db_index=True,
                default='draft',
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='published_at',
            field=models.DateTimeField(
                db_index=True,
                default=None,
                help_text='Controls when the post becomes publicly visible.',
            ),
        ),
        migrations.AlterModelOptions(
            name='blogpost',
            options={
                'ordering': ['-published_at', '-created_at'],
                'verbose_name': 'Blog post',
                'verbose_name_plural': 'Blog posts',
            },
        ),
    ]
