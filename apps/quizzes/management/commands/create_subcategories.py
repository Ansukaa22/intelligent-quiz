"""
Management command to create sample subcategories
"""

from django.core.management.base import BaseCommand
from apps.quizzes.models import Category, Subcategory
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Create sample subcategories for quiz categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample subcategories...')
        
        subcategories_data = {
            'Academic': [
                {'name': 'Python Programming', 'description': 'Test your Python coding knowledge'},
                {'name': 'JavaScript Basics', 'description': 'Learn and test JavaScript fundamentals'},
                {'name': 'Data Structures', 'description': 'Arrays, linked lists, trees, and more'},
                {'name': 'Algorithms', 'description': 'Sorting, searching, and algorithm complexity'},
                {'name': 'Web Development', 'description': 'HTML, CSS, and web technologies'},
            ],
            'Entertainment': [
                {'name': 'Movies & Cinema', 'description': 'Test your movie knowledge'},
                {'name': 'Music Trivia', 'description': 'Songs, artists, and music history'},
                {'name': 'TV Shows', 'description': 'Popular television series and shows'},
                {'name': 'Gaming', 'description': 'Video games and gaming culture'},
                {'name': 'Sports', 'description': 'Sports facts and trivia'},
            ],
            'General Knowledge': [
                {'name': 'World Geography', 'description': 'Countries, capitals, and landmarks'},
                {'name': 'History', 'description': 'Historical events and figures'},
                {'name': 'Science', 'description': 'Physics, chemistry, and biology'},
                {'name': 'Current Events', 'description': 'Recent news and happenings'},
                {'name': 'Literature', 'description': 'Books, authors, and literary works'},
            ],
        }
        
        created_count = 0
        
        for category_name, subcats in subcategories_data.items():
            try:
                category = Category.objects.get(name=category_name)
                
                for subcat_data in subcats:
                    slug = slugify(subcat_data['name'])
                    
                    subcategory, created = Subcategory.objects.get_or_create(
                        category=category,
                        slug=slug,
                        defaults={
                            'name': subcat_data['name'],
                            'description': subcat_data['description'],
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created: {category_name} -> {subcat_data["name"]}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'- Already exists: {category_name} -> {subcat_data["name"]}'
                            )
                        )
                
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Category not found: {category_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} new subcategories.'
            )
        )
