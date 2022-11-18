from email.mime import image
import re
import os
from unicodedata import name
from django.shortcuts import render
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.views.decorators.cache import cache_control
from django.db import connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from ocr.settings import MEDIA_ROOT
from pdf2image import convert_from_path
cursor=connection.cursor()

#Login Functionality
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if(request.method=='GET'):
        return render(request,'mysite/login.html')
    elif(request.method=='POST'):

        #Accept Username and Password from User and fetch data from database
        user_name=request.POST['user_name']
        user_password=request.POST['user_password']
        cursor.execute("Select * from user where name_user = '"+user_name+"' and password_user = '"+user_password+"' ")
        data=cursor.fetchall()

        #Grant access if username and password is in Database
        if data:
            request.session['user_name'] = user_name
            #Store access level as cookie for RBAC
            request.session['access_level'] = data[0][3]
            return HttpResponseRedirect('/home')
        else:
            return HttpResponseRedirect('/')
    
#Home Page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    if 'user_name' in request.session:
        cursor.execute("Select * from project")
        project_data = cursor.fetchall()
        number_of_projects=len(project_data)
        cursor.execute("Select * from user")
        user_data = cursor.fetchall()
        number_of_users=len(user_data)
        return render(request,'mysite/home.html',
        {'project_data':project_data,'user_data':user_data,'number_of_projects':number_of_projects,'number_of_users':number_of_users})
    else:
        return HttpResponseRedirect('/')    

#Project Tab
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def project(request):
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        cursor.execute("Select * from project")
        project_data = cursor.fetchall()
        return render(request,'mysite/project.html',{'project_data':project_data,'access_level':access_level})
    else:
        return HttpResponseRedirect('/')

#Add project
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_project(request):
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        if access_level=='5':
            if (request.method=='GET'):
                return render(request,'mysite/add_project.html')
            elif (request.method=='POST'):
                project_name=request.POST['project_name']
                project_description=request.POST['project_description']
                cursor.execute("Insert into project(name_project,description_project) values ('"+project_name+"','"+project_description+"')")
                return HttpResponseRedirect('/project')
        else:
            return HttpResponseRedirect('/project')
    else:
        return HttpResponseRedirect('/')

#Delete Project
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_project(request,project_id):
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        if access_level=='5':
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            cursor.execute("Delete from template where id_project="+str(project_id))
            cursor.execute("Delete from project where id_project ="+str(project_id))
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            return HttpResponseRedirect('/project')    
        else:
            return HttpResponseRedirect('/project')
    else:
        return HttpResponseRedirect('/')

#Update Project
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_project(request,project_id):
    if 'user_name' in request.session:
        if (request.method=='GET'):
            cursor.execute("Select * from project where id_project ="+str(project_id))
            project_details=cursor.fetchall()
            return render(request,'mysite/update_project.html',{'project_details':project_details[0]})
        elif(request.method=='POST'):
            project_name=request.POST['project_name']
            project_description=request.POST['project_description']
            cursor.execute("Update project set name_project='"+project_name+"', description_project='"+project_description+"' where id_project="+str(project_id))
            return HttpResponseRedirect('/project')
    else:
        return HttpResponseRedirect('/')

#Logout Functionality
def logout(request):
    del request.session['user_name']
    return HttpResponseRedirect('/')

#Gets all the template data from DB and renders the template.html page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def template(request):
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        cursor.execute("Select * from template")
        templates=cursor.fetchall() 
        #Specifies which function is called
        func='template'
        return render(request,'mysite/template.html',{'template_data':templates,'access_level':access_level,'function':func})
    else:    
        return HttpResponseRedirect('/')

#Gets specific Project's template data
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def project_template(request,project_id):
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        cursor.execute("Select * from template where id_project="+str(project_id))
        templates=cursor.fetchall()
        #Specifies which function is called
        func='project_template'
        return render(request,'mysite/template.html',{'template_data':templates,'access_level':access_level,'function':func})
    else:
        return HttpResponseRedirect('/')

#Adds new template
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_template(request):
    access_level=request.session.get('access_level')
    if 'user_name' in request.session:
        access_level=request.session.get('access_level')
        if access_level=='2' or access_level=='3' or access_level=='5':
            if(request.method=='GET'):
                cursor.execute("Select * from project")
                projects=cursor.fetchall()
                return render(request,'mysite/add_template.html',{'projects':projects})
            elif(request.method=='POST' and request.FILES['template_file']):

                #Getting template information from 'ADD TEMPLATE' form
                name_template=request.POST['template_name']
                description_template=request.POST['template_description']
                file_template=request.FILES['template_file']
                project_name=request.POST['name_project']

                #Getting file name in a variable and storing file in storage(media) folder
                name_file_template=str(file_template)
                path = default_storage.save('template/'+name_file_template+'', ContentFile(file_template.read()))
                template_path = os.path.join(settings.MEDIA_ROOT, path)

                #Getting Path of file in a variable to enter into database
                list1=template_path.split('\\')
                template_path="\\\\".join(list1)

                #Fetching ID of project
                cursor.execute("Select id_project from project where name_project= '"+project_name+"' ")
                id_project=cursor.fetchall()

                #Inserting Template details into Database
                cursor.execute("Insert into template(name_template,description_template,id_project,path_template) values('"+name_template+"','"+description_template+"','"+str(id_project[0][0])+"','"+template_path+"')")
                return HttpResponseRedirect('template')
        else:
            return HttpResponseRedirect('/template')
    else:
        return HttpResponseRedirect('/')

#Deletes Template
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_template(request,template_id):
    if 'user_name' in request.session:
        #Deleting template from database
        cursor.execute("Delete from template where id_template="+str(template_id))
        return HttpResponseRedirect('/template')
    else:
        return HttpResponseRedirect('/')

#Updates Template Details
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_template(request,template_id):
    if 'user_name' in request.session:
        if(request.method=='GET'):
            #Fetching data proir to updating to be used in form
            cursor.execute("Select * from template where id_template="+str(template_id))
            template_details=cursor.fetchall()
            return render(request,'mysite/update_template.html',{'template_details':template_details[0]})
        elif(request.method=='POST'):
            #Update details using form data
            name_template=request.POST['template_name']
            template_description=request.POST['template_description']
            cursor.execute("Update template set name_template='"+name_template+"', description_template='"+template_description+"' where id_template="+str(template_id))
            return HttpResponseRedirect('/template')
    else:
        return HttpResponseRedirect('/')

# def test(request):
#     return render(request,'mysite/test.html')

#Displays Template image
def display_template_file(request,template_id):
    if 'user_name' in request.session:
        #Getting Path of template file from the database
        cursor.execute("Select path_template from template where id_template="+str(template_id))
        template_path=cursor.fetchone()

        #Using RegEx to extract filename from file path and calculating file_name
        name_pattern = re.compile(r'(.+/)(.+)(\.pdf)')
        name_iter=name_pattern.findall(template_path[0])
        filename= name_iter[0][1]
        file_name=str(MEDIA_ROOT)+'\\images\\'+filename+'.png'
        image_path = filename+'.png'
        
        if os.path.exists(file_name):
            return render(request,'mysite/template_file.html',{'image_name':image_path})
        else:
            #Using PDF2IMAGE to convert pdf to image
            images = convert_from_path(template_path[0], poppler_path=r"C:\Program Files\poppler-0.68.0\bin",fmt='png')

            #Saving Image in media folder(image)
            images[0].save(file_name)
            return render(request,'mysite/template_file.html',{'image_name':image_path})
    else:
        return HttpResponseRedirect('/')
