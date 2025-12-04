from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Career, BlogCategory, BlogPost, BlogComment, Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate Careers, Blog Posts, Comments, and Example Users/Profiles'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting example data population..."))

        # -------------------
        # CAREERS
        # -------------------
        careers = [
            {
                "title": "Software Developer",
                "location": "Nairobi, Kenya",
                "job_type": "full_time",
                "description": "Join our engineering team to develop scalable web applications.",
                "requirements": "Python, Django, JavaScript, REST APIs, Git & Linux"
            },
            {
                "title": "IT Support Technician",
                "location": "Mombasa, Kenya",
                "job_type": "part_time",
                "description": "Manage customer support for WiFi installations and RouterOS configurations.",
                "requirements": "Networking basics, RouterOS, communication skills"
            },
            {
                "title": "Digital Marketing Manager",
                "location": "Remote",
                "job_type": "remote",
                "description": "Manage online campaigns, social media, SEO, and content strategy.",
                "requirements": "SEO, social media marketing, content strategy"
            },
            {
                "title": "UI/UX Designer",
                "location": "Nairobi, Kenya",
                "job_type": "full_time",
                "description": "Design beautiful and user-friendly interfaces for web and mobile apps.",
                "requirements": "Figma, Adobe XD, UI/UX design experience"
            },
        ]

        for cdata in careers:
            career, created = Career.objects.get_or_create(title=cdata["title"], defaults=cdata)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Career "{career.title}" created'))
            else:
                self.stdout.write(f'Career "{career.title}" already exists')

        # -------------------
        # BLOG CATEGORIES
        # -------------------
        categories = ["Programming", "Networking", "Technology Trends", "Web Development"]
        category_objs = {}
        for cat in categories:
            c, created = BlogCategory.objects.get_or_create(title=cat)
            category_objs[cat] = c
            if created:
                self.stdout.write(self.style.SUCCESS(f'Blog Category "{cat}" created'))

        # -------------------
        # BLOG POSTS
        # -------------------
        blogs = [
            {
                "title": "Introduction to Python Programming",
                "category": "Programming",
                "content": """Python is beginner-friendly and powerful. 
- What is Python?
- Why Python is beginner-friendly
- Installing Python
- Writing your first program"""
            },
            {
                "title": "How to Configure a MikroTik Router for Hotspot",
                "category": "Networking",
                "content": """Complete guide on MikroTik RouterOS hotspot setup:
- RouterOS installation
- Hotspot setup
- User Manager integration
- Voucher generation
- Captive portal customization"""
            },
            {
                "title": "The Future of Artificial Intelligence in Africa",
                "category": "Technology Trends",
                "content": """Africa is rapidly adopting AI in healthcare, fintech, education, and agriculture.
- Opportunities
- Case studies
- Challenges
- Future predictions"""
            },
            {
                "title": "Building a Django Website Step by Step",
                "category": "Web Development",
                "content": """Learn to build a fully functional Django website:
- Authentication
- Dashboards
- Blog system
- APIs"""
            },
        ]

        for b in blogs:
            post, created = BlogPost.objects.get_or_create(
                title=b["title"],
                defaults={
                    "category": category_objs[b["category"]],
                    "content": b["content"],
                    "published": True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Blog post "{post.title}" created'))
            else:
                self.stdout.write(f'Blog post "{post.title}" already exists')

        # -------------------
        # BLOG COMMENTS
        # -------------------
        comments = [
            {
                "post_title": "Introduction to Python Programming",
                "comments": [
                    {"name": "Alice", "comment": "Great introduction! Very easy to follow."},
                    {"name": "Bob", "comment": "Helped me start my first Python project. Thanks!"}
                ]
            },
            {
                "post_title": "How to Configure a MikroTik Router for Hotspot",
                "comments": [
                    {"name": "Charles", "comment": "Very detailed tutorial. Worked perfectly."},
                    {"name": "Diana", "comment": "Step-by-step instructions are excellent!"}
                ]
            },
            {
                "post_title": "The Future of Artificial Intelligence in Africa",
                "comments": [
                    {"name": "Eve", "comment": "Interesting insights on AI in Africa."},
                    {"name": "Frank", "comment": "Excited to see AI growth on the continent."}
                ]
            },
            {
                "post_title": "Building a Django Website Step by Step",
                "comments": [
                    {"name": "Grace", "comment": "Perfect for beginners!"},
                    {"name": "Henry", "comment": "Followed this guide and built my first Django site!"}
                ]
            }
        ]

        for c in comments:
            post = BlogPost.objects.get(title=c["post_title"])
            for com in c["comments"]:
                comment_obj, created = BlogComment.objects.get_or_create(
                    post=post,
                    name=com["name"],
                    comment=com["comment"]
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Comment by {com["name"]} added to "{post.title}"'))
                else:
                    self.stdout.write(f'Comment by {com["name"]} already exists for "{post.title}"')

        # -------------------
        # EXAMPLE USERS & PROFILES
        # -------------------
        example_users = [
            {"username": "user1", "full_name": "Alice Johnson", "points": 120},
            {"username": "user2", "full_name": "Bob Smith", "points": 250},
            {"username": "user3", "full_name": "Charles Kimani", "points": 80},
            {"username": "user4", "full_name": "Diana Mwangi", "points": 400},
        ]

        for udata in example_users:
            user, created = User.objects.get_or_create(
                username=udata["username"],
                defaults={"email": f'{udata["username"]}@example.com'}
            )
            if created:
                user.set_password("password123")  # default password
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created with password "password123"'))
            else:
                self.stdout.write(f'User "{user.username}" already exists')

            profile, prof_created = Profile.objects.get_or_create(user=user)
            profile.full_name = udata["full_name"]
            profile.points = udata["points"]
            profile.save()
            self.stdout.write(f'Profile for "{user.username}" set with {profile.points} points (Level {profile.level})')

        self.stdout.write(self.style.SUCCESS("All example data populated successfully!"))
