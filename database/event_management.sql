-- =====================================================
-- Paris Event Hub - Detailed PostgreSQL Schema
-- =====================================================

-- Drop existing tables (optional, for clean setup)
DROP TABLE IF EXISTS event_messages CASCADE;
DROP TABLE IF EXISTS waitlist CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS event_updates CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS event_ticket_types CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS event_categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =====================================================
-- 1. USERS
-- Stores both organizers and attendees using role field
-- =====================================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_role
        CHECK (role IN ('organizer', 'attendee'))
);

-- =====================================================
-- 2. EVENT_CATEGORIES
-- Master table for classifying events
-- =====================================================
CREATE TABLE event_categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- =====================================================
-- 3. EVENTS
-- Includes support for physical, virtual, and hybrid events
-- =====================================================
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    venue_address VARCHAR(255),
    virtual_link TEXT,
    capacity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    organizer_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_events_event_type
        CHECK (event_type IN ('physical', 'virtual', 'hybrid')),

    CONSTRAINT chk_events_status
        CHECK (status IN ('draft', 'published', 'cancelled', 'completed')),

    CONSTRAINT chk_events_capacity
        CHECK (capacity > 0),

    CONSTRAINT chk_events_time
        CHECK (end_time > start_time),

    -- Ensures correct fields are provided based on event type
    CONSTRAINT chk_events_location_rules
        CHECK (
            (event_type = 'physical' AND venue_address IS NOT NULL)
            OR
            (event_type = 'virtual' AND virtual_link IS NOT NULL)
            OR
            (event_type = 'hybrid' AND venue_address IS NOT NULL AND virtual_link IS NOT NULL)
        ),

    CONSTRAINT fk_events_organizer
        FOREIGN KEY (organizer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_events_category
        FOREIGN KEY (category_id)
        REFERENCES event_categories(id)
        ON DELETE RESTRICT
);

-- =====================================================
-- 4. EVENT_TICKET_TYPES
-- Supports multi-tier ticketing (VIP, Standard, Early Bird)
-- =====================================================
CREATE TABLE event_ticket_types (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    quota INTEGER NOT NULL,
    sales_start TIMESTAMP,
    sales_end TIMESTAMP,

    CONSTRAINT chk_ticket_price
        CHECK (price >= 0),

    CONSTRAINT chk_ticket_quota
        CHECK (quota > 0),

    CONSTRAINT chk_ticket_sales_period
        CHECK (
            sales_start IS NULL
            OR sales_end IS NULL
            OR sales_end > sales_start
        ),

    CONSTRAINT fk_ticket_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_ticket_name_per_event
        UNIQUE (event_id, name)
);

-- =====================================================
-- 5. BOOKINGS
-- Stores reservations made by users for events
-- =====================================================
CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    ticket_type_id BIGINT NOT NULL,
    booking_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',

    CONSTRAINT chk_bookings_status
        CHECK (status IN ('confirmed', 'cancelled')),

    CONSTRAINT fk_bookings_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_bookings_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_bookings_ticket_type
        FOREIGN KEY (ticket_type_id)
        REFERENCES event_ticket_types(id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_bookings_user_event
        UNIQUE (user_id, event_id)
);

-- =====================================================
-- 6. PAYMENTS
-- Stores payment information linked to bookings
-- =====================================================
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL UNIQUE,
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_ref VARCHAR(255) UNIQUE,
    paid_at TIMESTAMP,

    CONSTRAINT chk_payments_amount
        CHECK (amount >= 0),

    CONSTRAINT chk_payment_method
        CHECK (payment_method IN ('card', 'paypal', 'stripe', 'bank_transfer', 'cash')),

    CONSTRAINT chk_payment_status
        CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),

    CONSTRAINT fk_payments_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings(id)
        ON DELETE CASCADE
);

-- =====================================================
-- 7. REVIEWS
-- Stores user feedback for events
-- =====================================================
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_reviews_rating
        CHECK (rating BETWEEN 1 AND 5),

    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_reviews_user_event
        UNIQUE (user_id, event_id)
);

-- =====================================================
-- 8. EVENT_UPDATES
-- Stores event change history and announcements
-- =====================================================
CREATE TABLE event_updates (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    update_type VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_event_updates_type
        CHECK (
            update_type IN (
                'schedule_changed',
                'venue_changed',
                'cancelled',
                'agenda_updated',
                'speaker_changed',
                'general_announcement'
            )
        ),

    CONSTRAINT fk_event_updates_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE
);

-- =====================================================
-- 9. NOTIFICATIONS
-- Stores user-specific notifications related to events
-- =====================================================
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id BIGINT,
    type VARCHAR(30) NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_notifications_type
        CHECK (
            type IN (
                'booking_confirmed',
                'payment_success',
                'event_reminder',
                'event_cancelled',
                'event_updated',
                'waitlist_available'
            )
        ),

    CONSTRAINT fk_notifications_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_notifications_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE SET NULL
);

-- =====================================================
-- 10. WAITLIST
-- Stores users waiting for available slots when events are full
-- =====================================================
CREATE TABLE waitlist (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',

    CONSTRAINT chk_waitlist_status
        CHECK (status IN ('waiting', 'notified', 'converted', 'expired', 'cancelled')),

    CONSTRAINT fk_waitlist_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_waitlist_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_waitlist_user_event
        UNIQUE (user_id, event_id)
);

-- =====================================================
-- 11. EVENT_MESSAGES
-- Stores communication messages within events
-- =====================================================
CREATE TABLE event_messages (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    sender_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_event_messages_event
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_event_messages_sender
        FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);