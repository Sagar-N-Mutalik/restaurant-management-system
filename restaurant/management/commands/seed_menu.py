from django.core.management.base import BaseCommand
from restaurant.models import MenuItem, RestaurantTable

class Command(BaseCommand):
    help = 'Seeds the database with 50 realistic Indian fast-food items and 10 tables'

    def handle(self, *args, **kwargs):
        # 1. Clear existing Data
        self.stdout.write("Clearing old menu items and tables...")
        MenuItem.objects.all().delete()
        RestaurantTable.objects.all().delete()

        # 2. Re-create 10 Tables
        self.stdout.write("Creating 10 Restaurant Tables...")
        for i in range(1, 11):
            RestaurantTable.objects.create(table_number=i)

        # 3. Create 50 Menu Items (Prices in INR ₹)
        self.stdout.write("Creating 50 Menu Items...")
        
        items = [
            # 20 Pizzas
            {'name': 'Paneer Tikka Pizza', 'price': 349.00, 'item_type': 'VEG', 'description': 'Spicy paneer tikka with onions and capsicum.'},
            {'name': 'Tandoori Chicken Pizza', 'price': 449.00, 'item_type': 'NON_VEG', 'description': 'Classic tandoori chicken bits with mint mayo.'},
            {'name': 'Spicy Keema Pizza', 'price': 499.00, 'item_type': 'NON_VEG', 'description': 'Mutton keema laden with Indian spices and cheese.'},
            {'name': 'Margherita Pizza', 'price': 249.00, 'item_type': 'VEG', 'description': 'Classic cheese and tomato.'},
            {'name': 'Veg Extravaganza', 'price': 399.00, 'item_type': 'VEG', 'description': 'Loaded with black olives, capsicum, onion, grilled mushroom.'},
            {'name': 'Chicken Dominator', 'price': 549.00, 'item_type': 'NON_VEG', 'description': 'Double pepper barbecue chicken, peri-peri chicken, chicken tikka.'},
            {'name': 'Makhani Paneer Pizza', 'price': 379.00, 'item_type': 'VEG', 'description': 'Rich makhani sauce base with soft paneer cubes.'},
            {'name': 'Butter Chicken Pizza', 'price': 479.00, 'item_type': 'NON_VEG', 'description': 'Creamy butter chicken gravy base with roasted chicken.'},
            {'name': 'Vegan Delight Pizza', 'price': 329.00, 'item_type': 'VEGAN', 'description': 'Dairy-free cheese with spinach, mushrooms, and olives.'},
            {'name': 'Desi Masala Pizza', 'price': 299.00, 'item_type': 'VEG', 'description': 'Chatpata masala base with green chilies and onions.'},
            {'name': 'Mutton Rogan Josh Pizza', 'price': 599.00, 'item_type': 'NON_VEG', 'description': 'Kashmiri style mutton rogan josh on a thin crust.'},
            {'name': 'Chilli Paneer Pizza', 'price': 359.00, 'item_type': 'VEG', 'description': 'Indo-Chinese chilli paneer fusion pizza.'},
            {'name': 'Chicken Tikka Makhani Pizza', 'price': 489.00, 'item_type': 'NON_VEG', 'description': 'Blend of tikka and makhani flavors.'},
            {'name': 'Mushroom Tikka Pizza', 'price': 339.00, 'item_type': 'VEG', 'description': 'Tandoori mushrooms with fiery peppers.'},
            {'name': 'Cheesy Garlic Pizza', 'price': 279.00, 'item_type': 'VEG', 'description': 'Stuffed garlic bread transformed into a pizza.'},
            {'name': 'Prawn Balchao Pizza', 'price': 649.00, 'item_type': 'NON_VEG', 'description': 'Goan style spicy prawn pickle base.'},
            {'name': 'Palak Paneer Pizza', 'price': 369.00, 'item_type': 'VEG', 'description': 'Spinach base with garlic roasted paneer.'},
            {'name': 'Chicken Sausage Pizza', 'price': 399.00, 'item_type': 'NON_VEG', 'description': 'Loaded with spicy chicken sausages.'},
            {'name': 'Sweet Corn & Jalapeno', 'price': 289.00, 'item_type': 'VEG', 'description': 'Sweet and spicy mix.'},
            {'name': 'Vegan BBQ Jackfruit Pizza', 'price': 389.00, 'item_type': 'VEGAN', 'description': 'Pulled BBQ jackfruit with vegan mozzarella.'},

            # 10 Burgers
            {'name': 'Aloo Tikki Burger', 'price': 99.00, 'item_type': 'VEG', 'description': 'Crispy potato patty with Indian spices.'},
            {'name': 'Maharaja Mac (Veg)', 'price': 199.00, 'item_type': 'VEG', 'description': 'Double decker corn & cheese patty.'},
            {'name': 'Maharaja Mac (Chicken)', 'price': 249.00, 'item_type': 'NON_VEG', 'description': 'Double decker grilled chicken patty.'},
            {'name': 'Paneer Makhani Burger', 'price': 179.00, 'item_type': 'VEG', 'description': 'Paneer patty overloaded with makhani gravy.'},
            {'name': 'Spicy Chicken Burger', 'price': 149.00, 'item_type': 'NON_VEG', 'description': 'Crispy fried chicken with peri-peri mayo.'},
            {'name': 'Mutton Shami Burger', 'price': 299.00, 'item_type': 'NON_VEG', 'description': 'Authentic shami kebab in a brioche bun.'},
            {'name': 'Vegan Black Bean Burger', 'price': 189.00, 'item_type': 'VEGAN', 'description': 'Spicy black bean and lentil patty.'},
            {'name': 'Crispy Fish Burger', 'price': 229.00, 'item_type': 'NON_VEG', 'description': 'Amritsari style fried fish fillet.'},
            {'name': 'Tandoori Soya Burger', 'price': 159.00, 'item_type': 'VEG', 'description': 'High-protein tandoori soya chaap patty.'},
            {'name': 'Egg Bhurji Burger', 'price': 129.00, 'item_type': 'NON_VEG', 'description': 'Spicy scrambled eggs (bhurji) pav-style burger.'},

            # 10 Sides
            {'name': 'Masala Fries', 'price': 119.00, 'item_type': 'VEGAN', 'description': 'French fries tossed in chaat masala.'},
            {'name': 'Garlic Bread with Cheese', 'price': 149.00, 'item_type': 'VEG', 'description': 'Freshly baked with lots of mozzarella.'},
            {'name': 'Chicken Wings (Peri-Peri)', 'price': 249.00, 'item_type': 'NON_VEG', 'description': '6 pieces of spicy roasted wings.'},
            {'name': 'Paneer Tikka Skewers', 'price': 229.00, 'item_type': 'VEG', 'description': '4 pieces of tandoor roasted paneer.'},
            {'name': 'Mutton Seekh Kebab', 'price': 349.00, 'item_type': 'NON_VEG', 'description': 'Authentic minced mutton kebabs.'},
            {'name': 'Vegan Onion Rings', 'price': 139.00, 'item_type': 'VEGAN', 'description': 'Crispy battered onion rings.'},
            {'name': 'Cheesy Jalapeno Poppers', 'price': 179.00, 'item_type': 'VEG', 'description': 'Crumb fried cheese balls.'},
            {'name': 'Tandoori Chicken Nuggets', 'price': 199.00, 'item_type': 'NON_VEG', 'description': 'Nuggets marinated in tandoori spices.'},
            {'name': 'Corn & Cheese Samosa', 'price': 89.00, 'item_type': 'VEG', 'description': 'Mini samosas stuffed with corn and cheese.'},
            {'name': 'Gunpowder Potato Wedges', 'price': 129.00, 'item_type': 'VEGAN', 'description': 'Wedges tossed in South Indian gunpowder.'},

            # 10 Beverages
            {'name': 'Mango Lassi', 'price': 99.00, 'item_type': 'VEG', 'description': 'Thick and sweet yogurt drink with Alphonso mango.'},
            {'name': 'Masala Chai', 'price': 49.00, 'item_type': 'VEG', 'description': 'Authentic Indian spiced tea.'},
            {'name': 'Thums Up', 'price': 59.00, 'item_type': 'VEGAN', 'description': 'Taste the thunder.'},
            {'name': 'Cold Coffee', 'price': 149.00, 'item_type': 'VEG', 'description': 'Blended iced coffee with vanilla ice cream.'},
            {'name': 'Fresh Lime Soda (Sweet/Salt)', 'price': 79.00, 'item_type': 'VEGAN', 'description': 'Refreshing Nimbu Pani.'},
            {'name': 'Jaljeera', 'price': 69.00, 'item_type': 'VEGAN', 'description': 'Tangy cumin-based chilled drink.'},
            {'name': 'Rooh Afza Milkshake', 'price': 119.00, 'item_type': 'VEG', 'description': 'Rose syrup layered milkshake.'},
            {'name': 'Filter Coffee', 'price': 69.00, 'item_type': 'VEG', 'description': 'Strong South Indian drip coffee.'},
            {'name': 'Virgin Mojito', 'price': 129.00, 'item_type': 'VEGAN', 'description': 'Mint and lemon muddled with soda.'},
            {'name': 'Bottled Mineral Water', 'price': 20.00, 'item_type': 'VEGAN', 'description': '1 Liter.'},
        ]

        count = 0
        for item_data in items:
            MenuItem.objects.create(**item_data)
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} Menu Items!'))
        self.stdout.write(self.style.SUCCESS('Database Seeding Complete.'))
