# community/middleware.py
from django.utils import timezone
from datetime import date

class DailyActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Award daily login points
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                today = date.today()
                
                # Check if user logged in today
                if profile.last_login_date != today:
                    from .signals import award_points
                    
                    # Reset or update consecutive days
                    if profile.last_login_date and (today - profile.last_login_date).days == 1:
                        profile.consecutive_login_days += 1
                    else:
                        profile.consecutive_login_days = 1
                    
                    profile.last_login_date = today
                    profile.save()
                    
                    # Award daily login bonus
                    bonus_points = min(5, profile.consecutive_login_days)  # Max 5 points
                    award_points(request.user, bonus_points, f'Daily login bonus (Day {profile.consecutive_login_days})')
                    
                    # Award streak bonuses
                    if profile.consecutive_login_days % 7 == 0:  # Weekly bonus
                        award_points(request.user, 10, f'7-day login streak bonus')
                    if profile.consecutive_login_days % 30 == 0:  # Monthly bonus
                        award_points(request.user, 50, f'30-day login streak bonus')
                        
            except Exception as e:
                # Log error but don't break the app
                print(f"Error in DailyActivityMiddleware: {e}")
        
        return response