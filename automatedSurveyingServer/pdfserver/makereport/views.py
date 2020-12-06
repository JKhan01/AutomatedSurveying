from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from makereport.models import Projectdetails, Userdetails, Imagesdetails
from django.core.files.storage import FileSystemStorage
from makereport.helper import predictWater, predictSettle, predictNDVI
from weasyprint import HTML
from django.conf import settings
from django.template.loader import get_template
import pdfcrowd
# Create your views here.


def report(request,projectid):
    return HttpResponse('Kaam CHalu Aahe thamba')

def imageForm(request,projectId):
    if projectId:
        try:
            access = Projectdetails.objects.get(projectid=int(projectId))
            
            context = {'data':projectId}
            return render(request,'imageForm.html', context=context)
        except Exception as e:
            context = {'data':'Invalid Project ID. Avoid Making a direct GET request.'}
            return render(request,'error.html',context=context)
    
    context = {'data':'Bad Requested URL'}
    return render(request,'error.html',context=context)

def pushImage(request):
    if (request.method == 'POST'):
        projectId = request.POST['pid']
        imageList = request.FILES.getlist('imgs')
        try:

            count = 0
            print (imageList)
            for i in imageList:
                count += 1
                db = Imagesdetails(projectid=int(projectId),imagename=str(projectId)+"00"+str(count)+".jpg", height=float(0.0))
                db.save()
                store = FileSystemStorage()
                store.save(str(projectId)+ "00" + str(count)+".jpg",i)
                

            context = {"count":count,"pid":projectId}
            return render(request,'heightData.html',context=context)
        
        except Exception as e:
            context = {'data':str(e)}
            return render(request, "error.html", context=context)

    context = {'data':'Bad Request'}
    return render(request, "error.html", context=context)

def pushData(request):
    if (request.method == 'POST'):
        try:
            projectId = request.POST['pid']
            dataList = []
            for i in range(1,int(request.POST['length'])+1):
                obj = Imagesdetails(projectid=projectId,imagename=str(projectId) + "00" + str(i)+".jpg")
                obj.height = request.POST[f'{i}']
                obj.save()
                dataDict = {}
                dataDict["settle"] = predictSettle(projectId,i,float(request.POST[f'{i}']))
                dataDict["water"] = predictWater(projectId,i,float(request.POST[f'{i}']))
                dataDict["ndvi"] = predictNDVI(projectId,i,float(request.POST[f'{i}']))
                dataList.append(dataDict)
            context = {}
            context['projectid'] = projectId
            context['data'] = dataList
            access = Projectdetails.objects.get(projectid = projectId)
            context['projectname'] = access.projectname
            context['extent'] = access.extent
            context['count'] = int(request.POST['length'])
            
            # # return HttpResponseRedirect(rev)
            return render(request,'rawreport.html', context=context)
 
            
        except Exception as e:
            context = {'data':str(e)}
            return render(request, "error.html", context=context)

    context = {'data':'Bad Request'}
    return render(request, "error.html", context=context)



from django.template.defaulttags import register

@register.filter(name='get_range')
def get_range(value):
    return range(1,int(value)+1)