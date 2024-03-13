from django.shortcuts import render

# Create your views here.
def product_main(request):
    data ={ 

            }
    return render(request, 'main_products_app/main_products_app.html', context=data)
