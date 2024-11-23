from pydantic import BaseModel

class CreateStripeSubscription(BaseModel):
    price_id: str