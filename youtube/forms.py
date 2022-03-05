from django import forms



class youtube_download_form(forms.Form):
    link_field = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control rounded-0','id':'floatingInput','placeholder':'https://www.youtube.com/'}))
