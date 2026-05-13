from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, Category, TicketType, Booking
from django.contrib.auth.forms import UserCreationForm
from .models import Review
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

def home(request):
    events = Event.objects.all()
    return render(request, 'index.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def event_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only organizers with staff status can create events.")
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        quota = request.POST.get('quota')
        try:
            with transaction.atomic():
                category_obj = get_object_or_404(Category, id=category_id) if category_id else None
                new_event = Event.objects.create(
                    title=title, date=date, location=location,
                    category=category_obj, description="New Event Added!", organizer=request.user
                )
                if price and quota:
                    new_ticket = TicketType(
                        event=new_event, ticket_name="Standard",
                        price=price, quota=quota
                    )
                    new_ticket.full_clean()
                    new_ticket.save()
            return redirect('home')
        except Exception as e:
            return render(request, 'event_form.html', {'categories': categories, 'error_message': str(e)})
    return render(request, 'event_form.html', {'categories': categories})

@login_required
def event_booking(request, pk):
    event = get_object_or_404(Event, pk=pk)
    tickets = event.tickets.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                has_booking = False
                for ticket in tickets:
                    quantity = int(request.POST.get(f'qty_{ticket.id}', 0))
                    if quantity > 0:
                        if ticket.quota < quantity:
                            raise ValidationError(f"Not enough tickets for {ticket.ticket_name}")
                        Booking.objects.create(
                            user=request.user,
                            ticket_type=ticket,
                            quantity=quantity
                        )
                        ticket.quota -= quantity
                        ticket.save()
                        has_booking = True
                if has_booking:
                    return redirect('my_page')
                else:
                    return render(request, 'booking.html', {'event': event, 'tickets': tickets, 'error': 'Please select at least one ticket.'})
        except Exception as e:
            return render(request, 'booking.html', {'event': event, 'tickets': tickets, 'error': str(e)})
    return render(request, 'booking.html', {'event': event, 'tickets': tickets})

@login_required
def my_page(request):
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

    recent_bookings = bookings[:3]

    reviews = Review.objects.filter(booking__user=request.user)

    total_spent = sum(booking.total_price for booking in bookings)
    upcoming_count = bookings.count()

    return render(request, 'my_page.html', {
        'bookings': bookings,
        'recent_bookings': recent_bookings,
        'reviews': reviews,
        'total_spent': total_spent,
        'upcoming_count': upcoming_count
    })

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    categories = Category.objects.all()
    if event.organizer != request.user:
        return HttpResponseForbidden("You do not have permission to edit this event.")
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.date = request.POST.get('date')
        event.location = request.POST.get('location')
        category_id = request.POST.get('category')
        if category_id:
            event.category = get_object_or_404(Category, id=category_id)
        event.save()
        return redirect('event_detail', pk=event.pk)
    return render(request, 'event_form.html', {'event': event, 'categories': categories})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return HttpResponseForbidden("You do not have permission to delete this event.")
    if request.method == 'POST':
        event.delete()
        return redirect('home')
    return render(request, 'event_confirm_delete.html', {'event': event})



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    existing_review = Review.objects.filter(booking=booking).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')

        if existing_review:
            existing_review.rating = rating
            existing_review.content = content
            existing_review.save()
        else:
            Review.objects.create(
                booking=booking,
                rating=rating,
                content=content
            )
        return redirect('my_reviews')
        
    return render(request, 'review_form.html', {'booking': booking, 'existing_review': existing_review})


@login_required
def my_reviews(request):
    reviews = Review.objects.filter(booking__user=request.user).order_by('-created_at')
    return render(request, 'my_reviews.html', {'reviews': reviews})

@login_required
def profile_settings(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.save()
        return redirect('my_page')
        
    return render(request, 'profile.html')

@login_required
@require_POST
def delete_account(request):
    user = request.user

    if user.username == 'admin' or user.is_superuser:
        messages.error(request, "Admin accounts cannot be deleted for security reasons.")
        return redirect('profile_settings')

    user.delete()
    logout(request)
    messages.success(request, "Your account has been successfully deleted.")
    return redirect('home')
