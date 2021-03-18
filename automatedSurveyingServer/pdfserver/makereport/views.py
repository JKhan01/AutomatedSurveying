from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from makereport.models import Projectdetails, Userdetails, Imagesdetails
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, EmailMessage
from makereport.helper import predictWater, predictSettle, predictNDVI
from weasyprint import HTML
from django.conf import settings
from django.template.loader import get_template
from pdfserver.settings import FILE_URL, MEDIA_ROOT, STATIC_ROOT, STATIC_URL, MEDIA_URL, EMAIL_HOST_USER
import pdfcrowd
from xhtml2pdf import pisa
from io import BytesIO
import os

# Create your views here.


def report(request,projectid):
    try:
        return HttpResponseRedirect(f'http://127.0.0.1:8000/static/{projectid}report.pdf')
    except Exception as e:
        context = {'data':str(e)}
        return render(request, "error.html", context=context)
        

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

def pushData(request,pid,count):
    # if (request.method == 'POST'):
    try:
        # projectId = request.POST['pid']
        projectId = pid
        dataList = []
        # for i in range(1,int(request.POST['length'])+1):
        for i in range(1,int(count)):
            obj = Imagesdetails(projectid=projectId,imagename=str(projectId) + "00" + str(i)+".jpg")
            obj.height = 20
            obj.save()
            dataDict = {}
            dataDict["settle"] = predictSettle(projectId,i,float(20))
            dataDict["water"] = predictWater(projectId,i,float(20))
            dataDict["ndvi"] = predictNDVI(projectId,i,float(20))
            dataList.append(dataDict)
        context = {}
        context['projectid'] = projectId
        context['data'] = dataList
        access = Projectdetails.objects.get(projectid = projectId)
        context['projectname'] = access.projectname
        context['extent'] = access.extent
        context['count'] = int(count) - 1
        context['filePath'] = FILE_URL
        script = get_template('rawreport.html').render(context=context)
        # print (script)
        # pdfScript = HTML(string=str(script), base_url=str(MEDIA_ROOT))
        # pdfScript.write_pdf('makereport/static/'+projectId +"report.pdf")
        # # return HttpResponseRedirect(rev)
        # client = pdfcrowd.HtmlToPdfClient('jkhan01', '38fad4509b4556654673b7b7ac596269')

        # # run the conversion and write the result to a file
        # client.convertStringToFile(script, 'test.pdf') 
        result = BytesIO()
        script = script.replace('/static/',FILE_URL)
        # script = script.replace('vw','')
        # script = script.replace('vh','')
        # script = script.replace('%','')
        pdf = pisa.CreatePDF(script.encode('UTF-8'), open(f'makereport/static/{projectId}report.pdf','wb'))
        if not pdf.err:
            print ('jhala kahitari')
            f = FileSystemStorage()
            attach = f.open(f'{projectId}report.pdf')
            mail = EmailMessage(f"Survey Report for {context['projectname']}", 'Kindly find the requested survey report atatched to this email.', EMAIL_HOST_USER,['jkhan266@gmail.com'])
            mail.attach(attach.name, attach.read(), 'application/pdf')
            mail.send()
        else:
            print ('hagg diya')


        return render(request,'rawreport.html', context=context)

        
    except Exception as e:
        context = {'data':str(e)}
        return render(request, "error.html", context=context)

    # context = {'data':'Bad Request'}
    # return render(request, "error.html", context=context)


def test_post(request,pid):
    # if (request.method == 'POST'):

    if (pid == "3"):

        print ("nacho")
        return HttpResponse("Success")
    
    else:
        print ("haga")
        return HttpResponse("Haga")

from django.template.defaulttags import register

@register.filter(name='get_range')
def get_range(value):
    return range(1,int(value)+1)

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = STATIC_URL      # Typically /static/
    sRoot = STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = MEDIA_URL       # Typically /static/media/
    mRoot = MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                f'media URI must start with {sUrl} or {mUrl}'
            )
    return path