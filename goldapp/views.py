from django.shortcuts import render,HttpResponse
from .models import Merchant
from django.contrib import messages
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    merchant=Merchant.objects.all()
    query=""
    
    if request.method=='POST':
        if "add" in request.POST:
            name=request.POST.get('name')
            touch=request.POST.get('touch')
            Netwet=request.POST.get('Netwet')
            Gowet=request.POST.get('Gowet')
            pc=request.POST.get('PC')
            Item=request.POST.get('Item')
            Merchant.objects.create(
                name=name,
                touch=touch,
                Netwet=Netwet,
                Gowet=Gowet,
                PC=pc,
                Item=Item
            )
            messages.success(request,"Item added successfully")

        elif "update" in request.POST:
            id = request.POST.get("id")
            name = request.POST.get("name")
            touch = request.POST.get("touch")
            Netwet = request.POST.get("Netwet")
            Gowet = request.POST.get("Gowet")
            PC = request.POST.get("PC")
            Item = request.POST.get("Item")

            update_merchant = Merchant.objects.get(id=id)
            update_merchant.name = name
            update_merchant.touch = touch
            update_merchant.Netwet = Netwet
            update_merchant.Gowet = Gowet
            update_merchant.PC = PC
            update_merchant.Item = Item
            update_merchant.save()

            messages.success(request, "Merchant updated successfully")

        elif "delete" in request.POST:
            id=request.POST.get("id")
            Merchant.objects.get(id=id).delete()
            messages.success(request,"Item deleted successfully")

        elif "search" in request.POST:
            query=request.POST.get("searchquery")
            merchant=Merchant.objects.filter(Q(name__icontains=query)|Q(Item__icontains=query))

    context={'merchant':merchant,"query":query}
    return render(request,'index.html',context=context)

@csrf_exempt
def download_merchants_pdf(request):
    if request.method == 'POST':
        ids = request.POST.getlist('merchant_ids')
        merchants = Merchant.objects.filter(id__in=ids)
    else:
        merchants = Merchant.objects.none()
    template = get_template('goldapp/merchants_pdf.html')
    html = template.render({'merchants': merchants})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="merchants.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response
