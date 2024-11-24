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
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=["card"],
            line_items=[{"price": request.price_id, "quantity": 1}],
            mode="subscription",
            success_url="http://localhost:5173/dashboard/projects",
            cancel_url="http://localhost:5173/dashboard/subscription",
            metadata={
                "user_id": str(current_user.id)
            }
        )
        return checkout_session
    except InvalidRequestError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook", tags=["stripe"])
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    print(payload,request)
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="No Stripe signature found")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        
        match event.type:
            case "checkout.session.completed":

                subscription_id = event.data.object.get("subscription")
                user_id = event.data.object.get("metadata", {}).get("user_id")
                
                if user_id:
                    subscription = StripeSubscription(
                        user_id=user_id,
                        subscription_id=subscription_id,
                        status=SubscriptionStatus.active.value,
                        current_period_start=datetime.datetime.now()
                    )
                    db.add(subscription)
                    db.commit()
                    
            case "invoice.payment_succeeded":
                subscription_id = event.data.object.get("subscription")
                subscription = db.query(StripeSubscription).filter(
                    StripeSubscription.subscription_id == subscription_id
                ).first()
                
                if subscription:
                    subscription.status = SubscriptionStatus.active.value
                    subscription.current_period_start = datetime.datetime.fromtimestamp(
                        event.data.object.get("period_start")
                    )
                    db.commit()
                    
            case "customer.subscription.deleted":
                subscription_id = event.data.object.get("id")
                subscription = db.query(StripeSubscription).filter(
                    StripeSubscription.subscription_id == subscription_id
                ).first()
                
                if subscription:
                    subscription.status = SubscriptionStatus.inactive.value
                    db.commit()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
