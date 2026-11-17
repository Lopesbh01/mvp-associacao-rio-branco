from django.db import migrations

def criar_categorias(apps, schema_editor):
    Categoria = apps.get_model('solicitacoes', 'Categoria')
    for nome in ['Infraestrutura', 'Meio Ambiente', 'Manutenção', 'Esporte e Lazer', 'Iluminação pública', 'Limpeza urbana', 'Manutenção de calçadas', 'Praças e áreas públicas', 'Saneamento', 'Outros']:
        Categoria.objects.get_or_create(nome=nome)

def remover_categorias(apps, schema_editor):
    Categoria = apps.get_model('solicitacoes', 'Categoria')
    Categoria.objects.filter(nome__in=['Infraestrutura', 'Meio Ambiente', 'Manutenção', 'Esporte e Lazer', 'Iluminação pública', 'Limpeza urbana', 'Manutenção de calçadas', 'Praças e áreas públicas', 'Saneamento', 'Outros']).delete()

class Migration(migrations.Migration):
    dependencies = [('solicitacoes', '0001_initial')]
    operations = [migrations.RunPython(criar_categorias, remover_categorias)]
