from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('solicitacoes', '0002_categorias_iniciais')]
    operations = [
        migrations.CreateModel(
            name='TentativaLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_normalizado', models.CharField(max_length=254)),
                ('ip_digest', models.CharField(max_length=64)),
                ('tentativa_em', models.DateTimeField(auto_now_add=True)),
                ('sucesso', models.BooleanField(default=False)),
            ],
            options={'verbose_name': 'tentativa de autenticação', 'verbose_name_plural': 'tentativas de autenticação', 'ordering': ['-tentativa_em']},
        ),
        migrations.AddIndex(
            model_name='tentativalogin',
            index=models.Index(fields=['email_normalizado', 'ip_digest', 'tentativa_em'], name='tentativa_email_ip_1c8c7a_idx'),
        ),
    ]
