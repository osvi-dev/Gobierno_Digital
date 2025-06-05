import csv
from io import StringIO
from django.http import HttpResponse

def generar_users_csv(users):
    """
    Genera un archivo CSV a partir de una lista de usuarios.
    :param users: QuerySet o lista de objetos User de Django.
    :return: HttpResponse con el contenido del CSV.
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    writer.writerow(['id', 'email', 'first_name', 'last_name', 'phone', 'date_joined'])
    
    # Escribir datos de los usuarios
    for user in users:
        writer.writerow([
            user.id or '',
            user.email or '',
            user.first_name or '',
            user.last_name or '',
            user.phone or '',
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ''
        ])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    return response