from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, Category, TicketType, Booking, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_datetime

# --- 기본 뷰 ---
def home(request):
    today = timezone.localdate()
    events = Event.objects.filter(date__gte=today).annotate(total_tickets_sold=Sum('tickets__booking__quantity', default=0)).order_by('-total_tickets_sold')[:3]
    return render(request, 'index.html', {'events': events})

def view_all(request):
    today = timezone.localdate()
    return render(request, 'view_all.html', {
        'upcoming_events': Event.objects.filter(date__gte=today).order_by('date'),
        'past_events': Event.objects.filter(date__lt=today).order_by('-date')
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event, 'is_expired': event.date.date() < timezone.localdate()})

# --- 인증 뷰 ---
def user_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def signup(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect('home')
    return render(request, 'signup.html', {'form': form})

# --- 이벤트 및 예약 뷰 ---
@login_required
def event_create(request):
    if not request.user.groups.filter(name='Organizer').exists(): return HttpResponseForbidden()
    if request.method == 'POST':
        try:
            with transaction.atomic():
                new_event = Event.objects.create(
                    title=request.POST.get('title'), date=parse_datetime(request.POST.get('date')),
                    location=request.POST.get('location'), event_type=request.POST.get('eventType'),
                    meeting_link=request.POST.get('meeting_link'), category_id=request.POST.get('category'),
                    description=request.POST.get('description'), organizer=request.user, image=request.FILES.get('image')
                )
                for name, price, quota in zip(request.POST.getlist('ticket_name[]'), request.POST.getlist('ticket_price[]'), request.POST.getlist('ticket_quota[]')):
                    if name and price and quota: TicketType.objects.create(event=new_event, ticket_name=name, price=price, quota=quota)
            return redirect('home')
        except Exception as e: return render(request, 'event_form.html', {'error_message': str(e), 'categories': Category.objects.all()})
    return render(request, 'event_form.html', {'categories': Category.objects.all()})

@login_required
def event_booking(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                unique_code = f"BK-{request.user.id}-{int(timezone.now().timestamp())}"
                has_booking = False
                for ticket in event.tickets.all():
                    qty = int(request.POST.get(f'qty_{ticket.id}', 0))
                    if qty > 0:
                        Booking.objects.create(user=request.user, ticket_type=ticket, quantity=qty, order_code=unique_code, booked_at=timezone.now())
                        ticket.quota -= qty
                        ticket.save()
                        has_booking = True
                if has_booking: return redirect('my_page')
        except Exception as e: return render(request, 'booking.html', {'event': event, 'error': str(e)})
    return render(request, 'booking.html', {'event': event})

@login_required
def booking_detail(request, booking_id):
    target = get_object_or_404(Booking, id=booking_id, user=request.user)
    if not target.order_code: target.order_code = f"LEGACY-{target.booked_at.strftime('%Y%m%d%H%M%S')}"
    order_items = Booking.objects.filter(order_code=target.order_code, user=request.user).select_related('ticket_type')
    return render(request, 'booking_detail.html', {
        'booking': target, 'order_bookings': order_items,
        'total_order_price': sum(b.total_price for b in order_items), 'today': timezone.localdate()
    })

@login_required
def my_page(request):
    bookings = Booking.objects.filter(user=request.user).select_related('ticket_type__event').order_by('-booked_at')
    for b in bookings:
        if not b.order_code: b.order_code = f"LEGACY-{b.booked_at.strftime('%Y%m%d%H%M%S')}"
    unique_orders_count = bookings.values('order_code').distinct().count()
    reviews = Review.objects.filter(booking__user=request.user)
    return render(request, 'my_page.html', {
        'recent_bookings': bookings[:6], 'bookings': bookings,
        'total_events_count': unique_orders_count, 
        'today': timezone.localdate(),
        'reviews': reviews,
        'reviews_count': reviews.count(),
        'reviews_left_count': max(0, unique_orders_count - reviews.count())
    })

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.ticket_type.event.date <= timezone.now():
        messages.error(request, "You cannot cancel an event that has already started or passed.")
        return redirect('my_page')

    if request.method == 'POST':
        together_bookings = Booking.objects.filter(order_code=booking.order_code, user=request.user)
        
        with transaction.atomic():
            for b in together_bookings:
                if b.status != 'cancelled':
                    b.ticket_type.quota += b.quantity
                    b.ticket_type.save()
                    
                    b.status = 'cancelled'
                    b.save()
        
        messages.add_message(request, messages.SUCCESS, "Your booking has been successfully canceled.", extra_tags='toast')
        return redirect('my_page')
        
    return redirect('my_page')

@login_required
def my_tickets(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related(
            'ticket_type',
            'ticket_type__event',
            'ticket_type__event__category'
        )
        .order_by('-booked_at')
    )
    
    for b in bookings:
        if not b.order_code:
            b.order_code = f"LEGACY-{b.booked_at.strftime('%Y%m%d%H%M%S')}"
            
    unique_orders_count = bookings.values('order_code').distinct().count()
    reviews = Review.objects.filter(booking__user=request.user)
    
    return render(request, 'my_page.html', {
        'recent_bookings': bookings,
        'bookings': bookings,
        'show_all_tickets': True,
        'today': timezone.localdate(),
        'total_events_count': unique_orders_count,
        'reviews': reviews,
        'reviews_count': reviews.count(),
        'reviews_left_count': max(0, unique_orders_count - reviews.count())
    })

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.save()
        return redirect('event_detail', pk=pk)
    return render(request, 'event_form.html', {'event': event, 'categories': Category.objects.all()})

@login_required
def event_delete(request, pk):
    get_object_or_404(Event, pk=pk, organizer=request.user).delete()
    return redirect('home')

@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    review = Review.objects.filter(booking=booking).first()

    if request.method == 'POST':
        Review.objects.update_or_create(booking=booking, defaults={'rating': request.POST.get('rating'), 'content': request.POST.get('content')})
        return redirect('my_reviews')
    return render(request, 'review_form.html', {'booking': booking, 'existing_review': review})

@login_required
def my_reviews(request):
    return render(request, 'my_reviews.html', {'reviews': Review.objects.filter(booking__user=request.user)})

@login_required
def profile_settings(request):
    user = request.user
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.username = request.POST.get('name')
        if request.POST.get('password'): user.set_password(request.POST.get('password'))
        user.save()
        return redirect('my_page')
    return render(request, 'profile.html', {'user': user})

@login_required
@require_POST
def delete_account(request):
    request.user.delete()
    return redirect('home')

@login_required
@require_POST
def delete_review(request, review_id):
    get_object_or_404(Review, id=review_id, booking__user=request.user).delete()
    return redirect('my_reviews')

def event_search(request):
    query = request.GET.get('q')
    events = Event.objects.filter(title__icontains=query) if query else Event.objects.all()
    return render(request, 'search.html', {'events': events, 'query': query, 'total_count': events.count()})