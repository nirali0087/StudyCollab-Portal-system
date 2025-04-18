from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from . forms import * 
from .models import * 
from django.views import generic
from youtubesearchpython import VideosSearch 
import requests
from django.db.models import Q
import wikipedia 
import os
import google.generativeai as genai
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Configure Gemini AI API
genai.configure(api_key=settings.GEMINI_API_KEY) 

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
@login_required
def chatbot_response(request):
    response_text = ""
    user_input_text = ""
    
    if request.method == 'POST':
        user_input_text = request.POST.get('user_input', '')
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_input_text)

        # Remove '*' and '#' from the response text for non-code parts
        cleaned_response = response.text.replace('*', '')
        parts = cleaned_response.split('```')
        
        formatted_response = ""
        for i, part in enumerate(parts):
            if i % 2 == 1:
                # This is a code block, wrap it in a styled <pre><code> block
                formatted_response += f"<pre class='code-block'><code>{part.strip()}</code></pre>"
            else:
                # This is a non-code block (explanation), no special formatting
                formatted_response += f"<p>{part.strip()}</p>"

        response_text = formatted_response

    # Pass both the user question and bot response to the template
    return render(request, 'dashboard/chatbot.html', {'user_input_text': user_input_text, 'response_text': response_text})


@login_required
def home(request):
       return render(request, 'dashboard/home.html') 

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, f"Notes Added from {request.user.username} Successfully..!!")
    else:
        form = NotesForm()

    query = request.GET.get('q')
    if query:
        notes = Notes.objects.filter(user=request.user, title__icontains=query)
    else:
        notes = Notes.objects.filter(user=request.user)

    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required       
def delete_note(request,pk=None):
       Notes.objects.get(id=pk).delete()
       return redirect("notes")

@login_required  
def edit_note(request, pk):
    note = get_object_or_404(Notes, pk=pk)
    if request.method == "POST":
        form = NotesForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully!")
            return redirect('notes')
    else:
        form = NotesForm(instance=note)
    context = {'form': form, 'note': note}
    return render(request, 'dashboard/edit_note.html', context)

class NotesDetailview(generic.DetailView):
       model = Notes
       
@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            finished = request.POST.get('is_finished') == 'on'
            Homework.objects.create(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            messages.success(request, f'Homework added successfully!')
    else:
        form = HomeworkForm()
    
    homeworks = Homework.objects.filter(user=request.user)
    
    # Search
    query = request.GET.get('q', '')
    if query:
        homeworks = homeworks.filter(subject__icontains=query) | homeworks.filter(title__icontains=query)

    # Filter
    filter_status = request.GET.get('filter_status', '')
    if filter_status == 'completed':
        homeworks = homeworks.filter(is_finished=True)
    elif filter_status == 'not_completed':
        homeworks = homeworks.filter(is_finished=False)

    homework_done = not homeworks.exists()
    
    context = {
        'homeworks': homeworks,
        'homework_done': homework_done,
        'form': form
    }
    return render(request, 'dashboard/homework.html', context)
@login_required
def update_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk)
    homework.is_finished = not homework.is_finished
    homework.save()
    return redirect('homework')
@login_required
def delete_homework(request, pk=None):
    Homework.objects.filter(id=pk).delete()
    return redirect('homework')
@login_required
def edit_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk)
    if request.method == 'POST':
        form = HomeworkForm(request.POST, instance=homework)
        if form.is_valid():
            form.save()
            messages.success(request, f'Homework updated successfully!')
            return redirect('homework')
    else:
        form = HomeworkForm(instance=homework)
    
    return render(request, 'dashboard/homework_form.html', {'form': form})

def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST["text"]
        video = VideosSearch(text, limit=10)
        result_list = []
        
        for i in video.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published': i['publishedTime'],
            }
            desc = ''
            if i.get('descriptionSnippet'):
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
        
        context = {
            'form': form,
            'results': result_list,
        }
        return render(request, 'dashboard/youtube.html', context)
    
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, 'dashboard/youtube.html', context)
@login_required    
def todo(request):
    # Handle search query
    search_query = request.GET.get('search', '')

    # Handle filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'completed':
        todos = Todo.objects.filter(user=request.user, is_finished=True)
    elif status_filter == 'not_completed':
        todos = Todo.objects.filter(user=request.user, is_finished=False)
    else:
        todos = Todo.objects.filter(user=request.user)

    # Apply search filter if search_query is provided
    if search_query:
        todos = todos.filter(title__icontains=search_query)
    
    todos_done = not todos.exists()
    
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            finished = request.POST.get("is_finished", 'off') == 'on'
            Todo.objects.create(
                user=request.user,
                title=request.POST.get("title"),
                is_finished=finished
            )
            messages.success(request, f"To-do Added from {request.user.username}...!!")
            return redirect('todo')
    else:
        form = TodoForm()
    
    # Pass the search query to the context
    context = {
        'form': form,
        'todos': todos,
        'todos_done': todos_done,
        'search_form': DashboardForm(initial={'text': search_query}),
    }
    return render(request, 'dashboard/todo.html', context)
@login_required
def update_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, f"To-do Updated Successfully...!!")
            return redirect('todo')
    else:
        form = TodoForm(instance=todo)
    
    return render(request, 'dashboard/edit_todo.html', {'form': form, 'todo': todo})
@login_required
def delete_todo(request, pk=None):
    Todo.objects.filter(id=pk).delete()
    messages.success(request, f"To-do Deleted Successfully...!!")
    return redirect('todo')


def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST["text"]
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []

        for i in range(10):
            description = answer['items'][i]['volumeInfo'].get('description', '')
            truncated_description = description[:150] + '...' if len(description) > 300 else description  # Truncate description to 150 characters

            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': truncated_description,  # Use truncated description
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('averageRating'),  # Correct key
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,
        }
        return render(request, 'dashboard/books.html', context)

    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, 'dashboard/books.html', context)


def dictonary(request):
      if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST["text"]
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        try:
              phonetics = answer[0]['phonetics'][0]['text']
              audio = answer[0]['phonetics'][0]['audio']
              definition = answer[0]['meanings'][0]['definitions'][0]['definition']
              example = answer[0]['meanings'][0]['definitions'][0]['example']
              synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
              context = {
                    'form': form,
                    'input': text,
                    'phonetics': phonetics,
                    'audio' : audio,
                    'definition': definition,
                    'example': example,
                    'synonyms': synonyms,
              }
        except:
              context={
                    'form':form,
                    'input':''
              }
        return render(request, "dashboard/dictionary.html", context)
      else:      
        form = DashboardForm()
        context = {'form': form}
        return render(request, "dashboard/dictionary.html", context)
    

def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'links': search.url,
            'details':search.summary
        }
        return render(request, "dashboard/wiki.html", context)
    
    else:

        form = DashboardForm()
        context = {
        'form': form
               }
    return render(request, "dashboard/wiki.html", context)

def conversion(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversationLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and int(input_value) >= 0:
                    value = float(input_value)
                    if first == 'yard' and second == 'foot':
                        answer = f'{input_value} yard = {value * 3} foot'
                    elif first == 'foot' and second == 'yard':
                        answer = f'{input_value} foot = {value / 3} yard'
                   
                    elif first == 'inch' and second == 'meter':
                        answer = f'{input_value} inch = {value * 0.0254} meter'
                    elif first == 'meter' and second == 'inch':
                        answer = f'{input_value} meter = {value / 0.0254} inch'
                    elif first == 'mile' and second == 'kilometer':
                        answer = f'{input_value} mile = {value * 1.60934} kilometer'
                    elif first == 'kilometer' and second == 'mile':
                        answer = f'{input_value} kilometer = {value / 1.60934} mile'
   
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'answer': answer
                }

        elif request.POST['measurement'] == 'mass':
            measurement_form = ConversationMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and int(input_value) >= 0:
                    value = float(input_value)
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input_value} pound = {value * 0.453592} kilogram'
                    elif first == 'kilogram' and second == 'pound':
                        answer = f'{input_value} kilogram = {value * 2.20462} pound'
                    # Add more conditions here for new units
                    elif first == 'gram' and second == 'ounce':
                        answer = f'{input_value} gram = {value / 28.3495} ounce'
                    elif first == 'ounce' and second == 'gram':
                        answer = f'{input_value} ounce = {value * 28.3495} gram'
                    elif first == 'ton' and second == 'kilogram':
                        answer = f'{input_value} ton = {value * 907.185} kilogram'
                    elif first == 'kilogram' and second == 'ton':
                        answer = f'{input_value} kilogram = {value / 907.185} ton'
                    # Continue adding conversion logic for other units...

                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'answer': answer
                }
        elif request.POST['measurement'] == 'temperature':
            measurement_form = ConversationTemperatureForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    if first == 'celsius' and second == 'fahrenheit':
                        answer = f'{input_value} Celsius = {value * 9/5 + 32} Fahrenheit'
                    elif first == 'fahrenheit' and second == 'celsius':
                        answer = f'{input_value} Fahrenheit = {(value - 32) * 5/9} Celsius'
                    elif first == 'celsius' and second == 'kelvin':
                        answer = f'{input_value} Celsius = {value + 273.15} Kelvin'
                    elif first == 'kelvin' and second == 'celsius':
                        answer = f'{input_value} Kelvin = {value - 273.15} Celsius'
                    # Add more conversions if needed

                context['answer'] = answer

        elif request.POST['measurement'] == 'currency':
            measurement_form = ConversationCurrencyForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    # Hardcoded rates for demo purposes. In a real app, use an API.
                    conversion_rates = {
                        ('usd', 'eur'): 0.85,
                        ('eur', 'usd'): 1.18,
                        ('usd', 'inr'): 73.0,
                        ('inr', 'usd'): 0.014,
                        # Add more conversions here...
                    }
                    rate = conversion_rates.get((first, second), 1)
                    answer = f'{input_value} {first.upper()} = {value * rate} {second.upper()}'

                context['answer'] = answer
        elif request.POST['measurement'] == 'volume':
            measurement_form = ConversationVolumeForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    volume_conversions = {
                        ('ml', 'l'): value / 1000,
                        ('l', 'ml'): value * 1000,
                        ('cm³', 'l'): value / 1000,
                        ('l', 'cm³'): value * 1000,
                        ('gal', 'l'): value * 3.78541,
                        ('l', 'gal'): value / 3.78541,
                        ('pt', 'l'): value * 0.473176,
                        ('l', 'pt'): value / 0.473176,
                        ('qt', 'l'): value * 0.946353,
                        ('l', 'qt'): value / 0.946353,
                        ('fl oz', 'l'): value * 0.0295735,
                        ('l', 'fl oz'): value / 0.0295735,
                        # Add more conversions as needed...
                    }
                    result = volume_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        elif request.POST['measurement'] == 'area':
            measurement_form = ConversationAreaForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    area_conversions = {
                        ('mm²', 'cm²'): value / 100,
                        ('cm²', 'mm²'): value * 100,
                        ('cm²', 'm²'): value / 10000,
                        ('m²', 'cm²'): value * 10000,
                        ('m²', 'km²'): value / 1e6,
                        ('km²', 'm²'): value * 1e6,
                        ('ft²', 'm²'): value * 0.092903,
                        ('m²', 'ft²'): value / 0.092903,
                        ('yd²', 'm²'): value * 0.836127,
                        ('m²', 'yd²'): value / 0.836127,
                        ('acre', 'm²'): value * 4046.86,
                        ('m²', 'acre'): value / 4046.86,
                        ('hectare', 'm²'): value * 10000,
                        ('m²', 'hectare'): value / 10000,
                        # Add more conversions as needed...
                    }
                    result = area_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer
        elif request.POST['measurement'] == 'time':
            measurement_form = ConversationTimeForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    time_conversions = {
                        ('s', 'min'): value / 60,
                        ('min', 's'): value * 60,
                        ('min', 'h'): value / 60,
                        ('h', 'min'): value * 60,
                        ('h', 'days'): value / 24,
                        ('days', 'h'): value * 24,
                        ('days', 'weeks'): value / 7,
                        ('weeks', 'days'): value * 7,
                        ('weeks', 'months'): value / 4.34524,  # Approximation
                        ('months', 'weeks'): value * 4.34524,
                        ('months', 'years'): value / 12,
                        ('years', 'months'): value * 12,
                        # Add more as necessary...
                    }
                    result = time_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        # Angle Conversion
        elif request.POST['measurement'] == 'angle':
            measurement_form = ConversationAngleForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    angle_conversions = {
                        ('degrees', 'radians'): value * 0.0174533,
                        ('radians', 'degrees'): value / 0.0174533,
                        ('degrees', 'gradians'): value * 1.11111,
                        ('gradians', 'degrees'): value / 1.11111,
                        ('radians', 'gradians'): value * 63.662,
                        ('gradians', 'radians'): value / 63.662,
                        # Add more as necessary...
                    }
                    result = angle_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        # Pressure Conversion
        elif request.POST['measurement'] == 'pressure':
            measurement_form = ConversationPressureForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    pressure_conversions = {
                        ('Pa', 'kPa'): value / 1000,
                        ('kPa', 'Pa'): value * 1000,
                        ('kPa', 'bar'): value / 100,
                        ('bar', 'kPa'): value * 100,
                        ('bar', 'psi'): value * 14.5038,
                        ('psi', 'bar'): value / 14.5038,
                        ('atm', 'bar'): value * 1.01325,
                        ('bar', 'atm'): value / 1.01325,
                        ('atm', 'psi'): value * 14.696,
                        ('psi', 'atm'): value / 14.696,
                        # Add more as necessary...
                    }
                    result = pressure_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        elif request.POST['measurement'] == 'frequency':
            measurement_form = ConversationFrequencyForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    frequency_conversions = {
                        ('Hz', 'kHz'): value / 1000,
                        ('kHz', 'Hz'): value * 1000,
                        ('kHz', 'MHz'): value / 1000,
                        ('MHz', 'kHz'): value * 1000,
                        ('MHz', 'GHz'): value / 1000,
                        ('GHz', 'MHz'): value * 1000,
                        # Add more conversions as needed...
                    }
                    result = frequency_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        # New Force Conversion Logic
        elif request.POST['measurement'] == 'force':
            measurement_form = ConversationForceForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    force_conversions = {
                        ('N', 'kN'): value / 1000,
                        ('kN', 'N'): value * 1000,
                        ('N', 'lbf'): value * 0.224809,
                        ('lbf', 'N'): value / 0.224809,
                        ('dyn', 'N'): value / 1e5,
                        ('N', 'dyn'): value * 1e5,
                        # Add more conversions as needed...
                    }
                    result = force_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

        # New Digital Storage Conversion Logic
        elif request.POST['measurement'] == 'digital_storage':
            measurement_form = ConversationDigitalStorageForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and float(input_value) >= 0:
                    value = float(input_value)
                    digital_storage_conversions = {
                        ('b', 'B'): value / 8,
                        ('B', 'b'): value * 8,
                        ('B', 'KB'): value / 1024,
                        ('KB', 'B'): value * 1024,
                        ('KB', 'MB'): value / 1024,
                        ('MB', 'KB'): value * 1024,
                        ('MB', 'GB'): value / 1024,
                        ('GB', 'MB'): value * 1024,
                        ('GB', 'TB'): value / 1024,
                        ('TB', 'GB'): value * 1024,
                        # Add more conversions as needed...
                    }
                    result = digital_storage_conversions.get((first, second), 1)
                    answer = f'{input_value} {first} = {value * result} {second}'

                context['answer'] = answer

    else:
        form = ConversationForm()
        context = {'form': form, 'input': False}

    return render(request, "dashboard/conversion.html", context)


    
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')  # Save email
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account Created for {username}..!!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form
    }
    return render(request, "dashboard/register.html", context)

@login_required
def profile(request):
    homework = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    # Determine if homework and todos are done
    homework_done = len(homework) == 0
    todos_done = len(todos) == 0

    # Get user details
    user_email = request.user.email
    user_mobile = request.user.profile.mobile_number if hasattr(request.user, 'profile') else 'Not provided'
    username = request.user.username

    context = {
        'homeworks': homework,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done,
        'user_email': user_email,
        'user_mobile': user_mobile,
        'username': username,
    }

    return render(request, "dashboard/profile.html", context)
