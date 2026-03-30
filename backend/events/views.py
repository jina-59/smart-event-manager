from django.shortcuts import render

def home(request):
    # 우리가 설정한 frontend 폴더 안의 index.html을 읽어옵니다.
    return render(request, 'index.html')