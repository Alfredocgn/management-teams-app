import datetime
from time import timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from schemas.stripe_schema import CreateStripeSubscription
from config.security import get_current_user
from db.database import get_db
from sqlalchemy.orm import Session
from db.models import StripeSubscription, SubscriptionStatus, User
import stripe
import os
from stripe.error import InvalidRequestError, StripeError


router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def register_user_on_stripe(user: User, db: Session) -> User:
    
    subscription = db.query(StripeSubscription).filter(
        StripeSubscription.user_id == user.id
    ).first()
    
    if subscription and subscription.subscription_id:
        return user

    
    stripe_customer = stripe.Customer.create(name=user.first_name, email=user.email)
    
    
    if subscription:
        subscription.subscription_id = stripe_customer["id"]
    else:
        subscription = StripeSubscription(
            user_id=user.id,
            subscription_id=stripe_customer["id"],
            status=SubscriptionStatus.inactive.value
        )
        db.add(subscription)
    
    db.commit()
    db.refresh(subscription)
    return user

def create_datetime_from_stripe_timestamp(timestamp: float) -> datetime:
    datetime_with_stripe_timezone = datetime.fromtimestamp(
        timestamp, tz=timezone("America/Chihuahua")
    )
    return datetime_with_stripe_timezone.astimezone(timezone(os.getenv("TIME_ZONE")))


@router.get("/products", tags=["stripe"])
async def get_products(_: User= Depends(get_current_user)):
    try:
        products = stripe.Product.list(
            active=True,
            expand=['data.default_price']
        )

        formatted_products = [{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.default_price.unit_amount / 100 if product.default_price else None,
            'price_id': product.default_price.id
        } for product in products.data]

        return formatted_products

    except StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-checkout-session", tags=["stripe"])
async def create_checkout_session(
    request: CreateStripeSubscription,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
      
        user = register_user_on_stripe(current_user, db)
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{"price": request.price_id, "quantity": 1}],
            mode="subscription",
            success_url="http://localhost:5173/dashboard/projects",
            cancel_url="http://localhost:5173/dashboard/subscription",
            metadata={
                "user_id": str(current_user.id)
            }
        )
        print(checkout_session,'this is checkout')
        return checkout_session
    except InvalidRequestError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook", tags=["stripe"])
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    print("Webhook received!")
    print("Headers:", dict(request.headers))
    print("Payload:", payload.decode())
    print("Signature:", sig_header)
    
    if not sig_header:
        # For test events from Hookdeck
        if '"test":true' in payload.decode():
            return {"status": "success", "message": "Test event received"}
        raise HTTPException(status_code=400, detail="No Stripe signature found")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        
        print(f"Event type received: {event.type}")
        
        match event.type:
            case "checkout.session.completed":
                subscription_id = event.data.object.get("subscription")
                user_id = event.data.object.get("metadata", {}).get("user_id")
                
                if user_id:
                    existing_subscription = db.query(StripeSubscription).filter(
                        StripeSubscription.user_id == user_id
                    ).first()
                    
                    if existing_subscription:
                        existing_subscription.subscription_id = subscription_id
                        existing_subscription.status = SubscriptionStatus.active.value
                        existing_subscription.current_period_start = datetime.datetime.now()
                        db.commit()
                    else:
                        subscription = StripeSubscription(
                            user_id=user_id,
                            subscription_id=subscription_id,
                            status=SubscriptionStatus.active.value,
                            current_period_start=datetime.datetime.now()
                        )
                        db.add(subscription)
                        db.commit()
                    print(f"Subscription updated for user {user_id}")
            
            case "charge.updated":
                # Just log the event and return success
                print(f"Charge updated event received: {event.data.object.id}")
            
            case _:
                # Handle any other event type gracefully
                print(f"Unhandled event type: {event.type}")
                
        return {"status": "success", "type": event.type}
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        # Return 200 for events we don't need to handle
        # This prevents Stripe from retrying webhooks unnecessarily
        return {"status": "success", "message": "Event acknowledged"}