"""
Payment service for Razorpay integration
"""
from config import config
from utils.logger import payment_logger
from typing import Optional, Dict
import hashlib
import hmac

class RazorpayService:
    """Razorpay payment service"""
    
    def __init__(self):
        self.key_id = config.RAZORPAY_KEY_ID
        self.key_secret = config.RAZORPAY_KEY_SECRET
    
    def create_order(self, amount: float, currency: str = "INR", description: str = "", 
                    receipt: str = "", customer_notify: int = 1) -> Optional[Dict]:
        """Create Razorpay order"""
        try:
            import razorpay
            
            if not self.key_id or not self.key_secret:
                payment_logger.warning("Razorpay credentials not configured")
                return None
            
            client = razorpay.Client(auth=(self.key_id, self.key_secret))
            
            # Convert amount to paise (smallest unit)
            amount_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_paise,
                "currency": currency,
                "receipt": receipt,
                "description": description,
                "notes": {
                    "note_key_1": "E-Waste Management"
                }
            }
            
            order = client.order.create(data=order_data)
            payment_logger.info(f"Order created: {order['id']} for amount: {amount} {currency}")
            return order
        except Exception as e:
            payment_logger.error(f"Failed to create Razorpay order: {str(e)}")
            return None
    
    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, 
                                razorpay_signature: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            generated_signature = hmac.new(
                self.key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = generated_signature == razorpay_signature
            
            if is_valid:
                payment_logger.info(f"Payment signature verified for order: {razorpay_order_id}")
            else:
                payment_logger.warning(f"Invalid payment signature for order: {razorpay_order_id}")
            
            return is_valid
        except Exception as e:
            payment_logger.error(f"Failed to verify payment signature: {str(e)}")
            return False
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """Get payment details from Razorpay"""
        try:
            import razorpay
            
            client = razorpay.Client(auth=(self.key_id, self.key_secret))
            payment = client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            payment_logger.error(f"Failed to fetch payment details: {str(e)}")
            return None
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> Optional[Dict]:
        """Refund a payment"""
        try:
            import razorpay
            
            client = razorpay.Client(auth=(self.key_id, self.key_secret))
            
            refund_data = {}
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to paise
            
            refund = client.payment.refund(payment_id, refund_data)
            payment_logger.info(f"Refund initiated for payment: {payment_id}")
            return refund
        except Exception as e:
            payment_logger.error(f"Failed to refund payment: {str(e)}")
            return None

class PaymentService:
    """High-level payment service"""
    
    def __init__(self):
        self.razorpay = RazorpayService()
    
    def initiate_payment(self, submission_id: str, amount: float, 
                        customer_name: str, customer_email: str) -> Optional[Dict]:
        """Initiate payment for e-waste submission"""
        try:
            order = self.razorpay.create_order(
                amount=amount,
                currency="INR",
                description=f"E-Waste Incentive Payment - {submission_id}",
                receipt=submission_id,
                customer_notify=1
            )
            
            if order:
                payment_logger.info(f"Payment initiated for submission: {submission_id}")
                return {
                    "success": True,
                    "order_id": order["id"],
                    "amount": amount,
                    "customer_email": customer_email,
                    "customer_name": customer_name
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create payment order"
                }
        except Exception as e:
            payment_logger.error(f"Payment initiation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_payment_callback(self, razorpay_order_id: str, razorpay_payment_id: str,
                                razorpay_signature: str) -> Dict:
        """Process payment callback from Razorpay"""
        try:
            # Verify signature
            if not self.razorpay.verify_payment_signature(
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature
            ):
                return {
                    "success": False,
                    "error": "Invalid payment signature"
                }
            
            # Get payment details
            payment_details = self.razorpay.get_payment_details(razorpay_payment_id)
            
            if payment_details and payment_details.get("status") == "captured":
                payment_logger.info(f"Payment processed successfully: {razorpay_payment_id}")
                return {
                    "success": True,
                    "payment_id": razorpay_payment_id,
                    "order_id": razorpay_order_id,
                    "amount": payment_details.get("amount", 0) / 100,  # Convert from paise
                    "status": "completed"
                }
            else:
                return {
                    "success": False,
                    "error": "Payment not captured"
                }
        except Exception as e:
            payment_logger.error(f"Payment callback processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
payment_service = PaymentService()
