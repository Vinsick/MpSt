from django.shortcuts import render

def main(request):
    data ={ 

            }
    return render(request, 'main/main.html', context=data)
