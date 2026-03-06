from django.core.management.base import BaseCommand
from restaurant.models import RestaurantTable

class Command(BaseCommand):
    help = 'Seeds the database with 10 restaurant tables'

    def handle(self, *args, **kwargs):
        tables_created = 0
        for i in range(1, 11):
            table, created = RestaurantTable.objects.get_or_create(table_number=i)
            if created:
                tables_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created table {i}'))
            else:
                self.stdout.write(self.style.WARNING(f'Table {i} already exists'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {tables_created} tables'))
