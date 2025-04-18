from django import forms
from django.forms import widgets
from . models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class NotesForm(forms.ModelForm):
       class Meta:
              model = Notes
              fields = ['title', 'description']

class DateInput(forms.DateInput):
       input_type = 'date';

class HomeworkForm(forms.ModelForm):
       class Meta:
              model = Homework
              widgets = {'due':DateInput()}
              fields = ['subject', 'title', 'description','due', 'is_finished']


class DashboardForm(forms.Form):
       text = forms.CharField(max_length=100, label = "Enter Your Search: ")


class TodoForm(forms.ModelForm):
       class Meta:
              model = Todo
              fields = ['title', 'is_finished']

class ConversationForm(forms.Form):
    MEASUREMENTS = [
        ('length', 'Length'),
        ('mass', 'Mass'),
        ('temperature', 'Temperature'),
        ('currency', 'Currency'),
        ('volume', 'Volume'),
        ('area', 'Area'),
        ('time', 'Time'),
        ('angle', 'Angle'),
        ('pressure', 'Pressure'),
        ('frequency', 'Frequency'),
        ('force', 'Force'),
        ('digital_storage', 'Digital Storage')
    ]
    measurement = forms.CharField(
        label='Choose Measurement Type',
        widget=forms.Select(choices=MEASUREMENTS)
    )

class ConversationLengthForm(forms.Form):
    CHOICES = [
        ('yard', 'Yard (yd)'),
        ('foot', 'Foot (ft)'),
        ('inch', 'Inch (in)'),
        ('meter', 'Meter (m)'),
        ('kilometer', 'Kilometer (km)'),
        ('mile', 'Mile (mi)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationMassForm(forms.Form):
    CHOICES = [
        ('pound', 'Pound (lb)'),
        ('kilogram', 'Kilogram (kg)'),
        ('gram', 'Gram (g)'),
        ('ounce', 'Ounce (oz)'),
        ('ton', 'Ton (ton)')
    ]
    input = forms.CharField(
        required=False, label=False,
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationTemperatureForm(forms.Form):
    CHOICES = [
        ('celsius', 'Celsius (°C)'),
        ('fahrenheit', 'Fahrenheit (°F)'),
        ('kelvin', 'Kelvin (K)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationCurrencyForm(forms.Form):
    CHOICES = [
        ('usd', 'USD (US dollars)'),
        ('eur', 'EUR (Euro)'),
        ('inr', 'INR (Indian Ruppe)'),
        ('gbp', 'GBP (British Pound)')
    ]
    input = forms.CharField(
        required=False, label=False,
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Amount'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationVolumeForm(forms.Form):
    CHOICES = [
        ('ml', 'Milliliter (ml)'),
        ('l', 'Liter (L)'),
        ('m³', 'Cubic Meter (m³)'),
        ('cm³', 'Cubic Centimeter (cm³)'),
        ('gal', 'Gallon (gal)'),
        ('pt', 'Pint (pt)'),
        ('qt', 'Quart (qt)'),
        ('fl oz', 'Fluid Ounce (fl oz)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationAreaForm(forms.Form):
    CHOICES = [
        ('mm²', 'Square Millimeter (mm²)'),
        ('cm²', 'Square Centimeter (cm²)'),
        ('m²', 'Square Meter (m²)'),
        ('km²', 'Square Kilometer (km²)' ),
        ('ft²', 'Square Foot (ft²)'),
        ('yd²', 'Square Yard (yd²)'),
        ('acre', 'Acre'),
        ('hectare', 'Hectare')
    ]
    input = forms.CharField(
        required=False, label=False,
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationTimeForm(forms.Form):
    CHOICES = [
        ('s', 'Seconds'),
        ('min', 'Minutes'),
        ('h', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationAngleForm(forms.Form):
    CHOICES = [
        ('degrees', 'Degrees (°)'),
        ('radians', 'Radians (rad)'),
        ('gradians', 'Gradians (gon)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationPressureForm(forms.Form):
    CHOICES = [
        ('Pa', 'Pascal (Pa)'),
        ('kPa', 'Kilopascal (kPa)'),
        ('bar', 'Bar'),
        ('psi', 'PSI'),
        ('atm', 'Atmosphere (atm)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Number'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )


class ConversationFrequencyForm(forms.Form):
    CHOICES = [
        ('Hz', 'Hertz (Hz)'),
        ('kHz', 'Kilohertz (kHz)'),
        ('MHz', 'Megahertz (MHz)'),
        ('GHz', 'Gigahertz (GHz)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Frequency'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationForceForm(forms.Form):
    CHOICES = [
        ('N', 'Newton (N)'),
        ('kN', 'Kilonewton (kN)'),
        ('lbf', 'Pound-Force (lbf)'),
        ('dyn', 'Dyne (dyn)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Force'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )

class ConversationDigitalStorageForm(forms.Form):
    CHOICES = [
        ('b', 'Bits (b)'),
        ('B', 'Bytes (B)'),
        ('KB', 'Kilobytes (KB)'),
        ('MB', 'Megabytes (MB)'),
        ('GB', 'Gigabytes (GB)'),
        ('TB', 'Terabytes (TB)')
    ]
    input = forms.CharField(
        required=False, label=False, 
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': 'Enter the Digital Storage'})
    )
    measure1 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )
    measure2 = forms.CharField(
        label='', widget=forms.Select(choices=CHOICES)
    )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'password1', 'password2']