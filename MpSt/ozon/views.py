from django.shortcuts import render

def ozon_main(request):
    data ={ 

            }
    return render(request, 'ozon/main.html', context=data)
