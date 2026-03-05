import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_door.settings')
django.setup()

from door.models import User

def promote_to_admin(username):
    try:
        user = User.objects.get(username=username)
        user.is_admin = True
        user.is_approved = True
        user.save()
        print(f"Successfully promoted '{username}' to Admin.")
    except User.DoesNotExist:
        print(f"User '{username}' not found.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        promote_to_admin(sys.argv[1])
    else:
        print("Usage: python promote_admin.py <username>")
