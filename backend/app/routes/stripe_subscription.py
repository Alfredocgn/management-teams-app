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
    if user.stripe_customer_id is not None:
        return user

    stripe_customer = stripe.Customer.create(name=user.first_name, email=user.email)
    user.stripe_customer_id = stripe_customer["id"]
    db.commit()
    db.refresh(user)

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
async def create_checkout_session(request: CreateStripeSubscription,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  stripe_user = register_user_on_stripe(current_user, db)
  try:
    checkout_session = stripe.checkout.Session.create(
      customer=stripe_user.stripe_customer_id,
    payment_method_types=["card"],
    line_items=[{"price":request.price_id, "quantity":1}],
    mode="subscription",
    success_url="https://example.com/success",
    cancel_url="https://example.com/cancel",
  )
    return checkout_session
  except InvalidRequestError as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook", tags=["stripe"])
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):


  event = stripe.Webhook.construct_event(
        payload=await request.body(),
        sig_header=request.headers["stripe_signature"],
        secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
    )
  user = db.query(User).filter(User.stripe_customer_id == event["data"]["object"]["customer"]).first()
  event_type = event["type"]

  match event_type:
    case "invoice.payment_succeeded":
      current_period_start = create_datetime_from_stripe_timestamp(
                event.data.object["period_start"]
            )
      subscription_id = event.data.object["subscription"]

      subscription = db.query(StripeSubscription).filter(StripeSubscription.subscription_id == subscription_id).one_or_none()

      if subscription:
        subscription.status = SubscriptionStatus.active.value
        subscription.current_period_start = current_period_start
        db.commit()
        db.refresh(subscription)
      else:
        new_subscription = StripeSubscription(
          subscription_id=subscription_id,
          status=SubscriptionStatus.active.value,
          current_period_start=current_period_start,
          user_id=user.id
        )
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)

    case "customer.subscription.deleted":
      subscription = db.query(StripeSubscription).filter(StripeSubscription.subscription_id == event.data.object["id"]).first()
      if subscription:
        subscription.status = SubscriptionStatus.inactive.value
        db.commit()
        db.refresh(subscription)
        #send email to user notifying that the subscription has been deleted / ended

    case "invoice.upcoming":
      # send email to user notifying that the subscription is going to be ended soon
      pass