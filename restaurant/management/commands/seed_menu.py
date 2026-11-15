from django.core.management.base import BaseCommand
from restaurant.models import MenuItem, RestaurantTable

class Command(BaseCommand):
    help = 'Seeds the database with 50 affordable, student-friendly Indian fast-food items and 10 tables'

    def handle(self, *args, **kwargs):
        # 1. Clear existing Data
        self.stdout.write("Clearing old menu items and tables...")
        MenuItem.objects.all().delete()
        RestaurantTable.objects.all().delete()

        # 2. Re-create 10 Tables
        self.stdout.write("Creating 10 Restaurant Tables...")
        for i in range(1, 11):
            RestaurantTable.objects.create(table_number=i)

        # 3. Create 50 Menu Items with affordable, student-friendly prices (Prices in INR ₹)
        self.stdout.write("Creating 50 Affordable Menu Items...")
        
        items = [
            # 20 Pizzas (Affordable Student Prices: ₹89 - ₹179)
            {'name': 'Margherita Pizza', 'price': 89.00, 'item_type': 'VEG', 'description': 'Classic mozzarella cheese and fresh basil-infused tomato sauce on thin crust.'},
            {'name': 'Sweet Corn & Jalapeno Pizza', 'price': 99.00, 'item_type': 'VEG', 'description': 'Golden sweet corn paired with zesty pickled jalapenos and melted cheese.'},
            {'name': 'Desi Masala Pizza', 'price': 99.00, 'item_type': 'VEG', 'description': 'Chatpata Indian spiced tomato base with crunchy onions and green capsicum.'},
            {'name': 'Cheesy Garlic Pizza', 'price': 109.00, 'item_type': 'VEG', 'description': 'Garlic butter crust loaded with herbs and golden mozzarella blend.'},
            {'name': 'Mushroom Tikka Pizza', 'price': 119.00, 'item_type': 'VEG', 'description': 'Tandoori-spiced button mushrooms, roasted bell peppers, and oregano.'},
            {'name': 'Palak Paneer Pizza', 'price': 119.00, 'item_type': 'VEG', 'description': 'Pureed spinach base, garlic roasted paneer cubes, and fresh herbs.'},
            {'name': 'Vegan Delight Pizza', 'price': 119.00, 'item_type': 'VEGAN', 'description': 'Dairy-free cheese, grilled zucchini, baby spinach, and kalamata olives.'},
            {'name': 'Paneer Tikka Pizza', 'price': 129.00, 'item_type': 'VEG', 'description': 'Char-grilled cottage cheese tikka cubes with sliced onions and capsicum.'},
            {'name': 'Chilli Paneer Pizza', 'price': 129.00, 'item_type': 'VEG', 'description': 'Indo-Chinese fusion pizza with soy-glazed paneer and fiery green chilies.'},
            {'name': 'Vegan BBQ Jackfruit Pizza', 'price': 129.00, 'item_type': 'VEGAN', 'description': 'Pulled tender jackfruit in smoky BBQ glaze with vegan mozzarella.'},
            {'name': 'Veg Extravaganza', 'price': 139.00, 'item_type': 'VEG', 'description': 'Loaded with black olives, crisp capsicum, diced onion, and grilled mushrooms.'},
            {'name': 'Makhani Paneer Pizza', 'price': 139.00, 'item_type': 'VEG', 'description': 'Rich buttery makhani sauce base crowned with tender malai paneer.'},
            {'name': 'Chicken Sausage Pizza', 'price': 139.00, 'item_type': 'NON_VEG', 'description': 'Sliced spiced chicken sausages, paprika, and stretchy mozzarella cheese.'},
            {'name': 'Tandoori Chicken Pizza', 'price': 149.00, 'item_type': 'NON_VEG', 'description': 'Clay-oven tandoori chicken chunks with mint swirl and crunchy onions.'},
            {'name': 'Butter Chicken Pizza', 'price': 159.00, 'item_type': 'NON_VEG', 'description': 'Velvety makhani gravy base topped with aromatic roasted butter chicken.'},
            {'name': 'Spicy Keema Pizza', 'price': 159.00, 'item_type': 'NON_VEG', 'description': 'Slow-cooked spiced minced keema with caramelized onions and green chilies.'},
            {'name': 'Chicken Tikka Makhani Pizza', 'price': 159.00, 'item_type': 'NON_VEG', 'description': 'Smoky chicken tikka glazed in rich makhani sauce with fresh coriander.'},
            {'name': 'Chicken Dominator', 'price': 169.00, 'item_type': 'NON_VEG', 'description': 'Barbecue pepper chicken, peri-peri chicken chunks, and herb chicken tikka.'},
            {'name': 'Mutton Rogan Josh Pizza', 'price': 179.00, 'item_type': 'NON_VEG', 'description': 'Kashmiri style aromatic tender mutton shreds on hand-tossed crust.'},
            {'name': 'Prawn Balchao Pizza', 'price': 189.00, 'item_type': 'NON_VEG', 'description': 'Coastal Goan style tangy spiced prawns with roasted garlic and cheese.'},

            # 10 Burgers (Affordable Student Prices: ₹39 - ₹99)
            {'name': 'Aloo Tikki Burger', 'price': 39.00, 'item_type': 'VEG', 'description': 'Crispy spiced potato & green pea patty topped with tangy mint sauce.'},
            {'name': 'Egg Bhurji Burger', 'price': 49.00, 'item_type': 'NON_VEG', 'description': 'Spicy scrambled eggs tempered with onions, tomatoes, and butter-toasted bun.'},
            {'name': 'Tandoori Soya Burger', 'price': 59.00, 'item_type': 'VEG', 'description': 'High-protein tandoori soya chaap patty with crunchy lettuce and mayo.'},
            {'name': 'Spicy Chicken Burger', 'price': 69.00, 'item_type': 'NON_VEG', 'description': 'Golden fried chicken fillet seasoned with fiery peri-peri spices and slaw.'},
            {'name': 'Paneer Makhani Burger', 'price': 69.00, 'item_type': 'VEG', 'description': 'Thick paneer slice drenched in velvety makhani sauce and sliced tomatoes.'},
            {'name': 'Vegan Black Bean Burger', 'price': 69.00, 'item_type': 'VEGAN', 'description': 'Handcrafted seasoned black bean & brown lentil patty with vegan garlic aioli.'},
            {'name': 'Maharaja Mac (Veg)', 'price': 79.00, 'item_type': 'VEG', 'description': 'Double-decker corn, cheese & potato patties with signature thousand island sauce.'},
            {'name': 'Maharaja Mac (Chicken)', 'price': 89.00, 'item_type': 'NON_VEG', 'description': 'Double grilled chicken patties layered with cheese slice and crunchy pickles.'},
            {'name': 'Crispy Fish Burger', 'price': 89.00, 'item_type': 'NON_VEG', 'description': 'Amritsari spiced crispy fish fillet served with dill tartar sauce.'},
            {'name': 'Mutton Shami Burger', 'price': 99.00, 'item_type': 'NON_VEG', 'description': 'Melt-in-mouth royal mutton shami kebab nestled in warm brioche bun.'},

            # 10 Appetizers & Sides (Affordable Student Prices: ₹29 - ₹89)
            {'name': 'Corn & Cheese Samosa', 'price': 29.00, 'item_type': 'VEG', 'description': 'Two golden crisp mini samosas overflowing with sweet corn and melted cheese.'},
            {'name': 'Masala Fries', 'price': 39.00, 'item_type': 'VEGAN', 'description': 'Golden crinkle fries generously dusted with street-style chaat masala.'},
            {'name': 'Gunpowder Potato Wedges', 'price': 45.00, 'item_type': 'VEGAN', 'description': 'Rustic potato wedges tossed in spicy South Indian podi gunpowder.'},
            {'name': 'Vegan Onion Rings', 'price': 49.00, 'item_type': 'VEGAN', 'description': 'Crispy tempura-battered sweet onion rings served with tangy dip.'},
            {'name': 'Garlic Bread with Cheese', 'price': 59.00, 'item_type': 'VEG', 'description': 'Toasted French baguette spread with garlic herb butter and bubbling mozzarella.'},
            {'name': 'Cheesy Jalapeno Poppers', 'price': 59.00, 'item_type': 'VEG', 'description': 'Golden crumb-fried cheese spheres bursting with spicy diced jalapenos.'},
            {'name': 'Paneer Tikka Skewers', 'price': 69.00, 'item_type': 'VEG', 'description': 'Three skewers of smoky tandoor-roasted paneer, peppers, and onions.'},
            {'name': 'Tandoori Chicken Nuggets', 'price': 69.00, 'item_type': 'NON_VEG', 'description': 'Bite-sized chicken nuggets steeped in traditional yogurt tandoori marinade.'},
            {'name': 'Chicken Wings (Peri-Peri)', 'price': 79.00, 'item_type': 'NON_VEG', 'description': 'Four succulent roasted wings glazed in spicy African bird eye chili sauce.'},
            {'name': 'Mutton Seekh Kebab', 'price': 89.00, 'item_type': 'NON_VEG', 'description': 'Juicy minced mutton skewers infused with mint, ginger, and royal spices.'},

            # 10 Beverages (Affordable Student Prices: ₹15 - ₹49)
            {'name': 'Bottled Mineral Water', 'price': 15.00, 'item_type': 'VEGAN', 'description': 'Chilled packaged 1 Litre mineral water.'},
            {'name': 'Masala Chai', 'price': 15.00, 'item_type': 'VEG', 'description': 'Authentic street-style brewed tea infused with ginger, cardamom, and clove.'},
            {'name': 'Filter Coffee', 'price': 20.00, 'item_type': 'VEG', 'description': 'Traditional South Indian frothy chicory drip coffee in tumbler.'},
            {'name': 'Thums Up', 'price': 25.00, 'item_type': 'VEGAN', 'description': 'Ice-cold 300ml bottled strong Indian cola.'},
            {'name': 'Jaljeera', 'price': 25.00, 'item_type': 'VEGAN', 'description': 'Digestive chilled cooler seasoned with roasted cumin, rock salt, and mint.'},
            {'name': 'Fresh Lime Soda (Sweet/Salt)', 'price': 30.00, 'item_type': 'VEGAN', 'description': 'Fizzy thirst-quencher with freshly squeezed lemons and sparkling soda.'},
            {'name': 'Mango Lassi', 'price': 35.00, 'item_type': 'VEG', 'description': 'Thick and creamy churned yogurt blended with ripe Alphonso mango pulp.'},
            {'name': 'Rooh Afza Milkshake', 'price': 40.00, 'item_type': 'VEG', 'description': 'Chilled fragrant rose syrup milkshake served with sabja seeds.'},
            {'name': 'Cold Coffee', 'price': 45.00, 'item_type': 'VEG', 'description': 'Thick blended iced coffee crowned with a dollop of vanilla cream.'},
            {'name': 'Virgin Mojito', 'price': 45.00, 'item_type': 'VEGAN', 'description': 'Muddled fresh mint leaves, lime wedges, and cane sugar with crisp club soda.'},
        ]

        count = 0
        for item_data in items:
            MenuItem.objects.create(**item_data)
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} Affordable Menu Items!'))
        self.stdout.write(self.style.SUCCESS('Database Seeding Complete.'))
