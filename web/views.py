from multiprocessing import context
from django.shortcuts import render
import razorpay
from .models import Order
from django.views.decorators.csrf import csrf_exempt
from .constants import PaymentStatus
import json
# Create your views here.

def index(request):
    
    return render(request,'index.html')

def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        client = razorpay.Client(auth=("rzp_test_D9KXF2jonrzG2O", "WiqGn58jJE0BOfHZtXpTDRa6"))
        razorpay_order = client.order.create({"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"})
        order = Order.objects.create(name=name, amount=amount, provider_order_id=razorpay_order["id"])
        order.save()
        return render(
            request,
            "payment.html",
            {
                "callback_url": "https://" + "razorpaytask.herokuapp.com" + "/callback/",
                "razorpay_key": 'rzp_test_D9KXF2jonrzG2O',
                "order": order,
            },
        )
    return render(request, "payment.html")



@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=("rzp_test_D9KXF2jonrzG2O", "WiqGn58jJE0BOfHZtXpTDRa6"))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "callback.html", context={"status": order.status})
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error")).get("order_id")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "payment.html")



