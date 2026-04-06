from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, Category, TicketType, Booking

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
    # 사용자가 예약한 모든 내역을 가져옴
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    
    # 📍 [수정] 통계 수치 실시간 계산 로직 추가
    # 1. 모든 예약의 총 가격 합산 (모델에 정의한 total_price 속성 사용)
    total_spent = sum(booking.total_price for booking in bookings)
    
    # 2. 예약 건수 자체가 다가올 예약(Upcoming) 수라면 동일하게 적용
    upcoming_count = bookings.count()

    return render(request, 'my_page.html', {
        'bookings': bookings,
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