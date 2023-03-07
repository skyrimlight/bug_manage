# from mobile import models
from django import forms


class BootStrap:
    bootstrap_exclude_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.fields.items():
            if key in self.bootstrap_exclude_fields:
                continue
            # value.widget.attrs['class'] = "form-control"
            # value.widget.attrs['placeholder'] = value.label
            old_class = value.widget.attrs.get('class', '')
            #
            # if value.widget.attrs:
            #     value.widget.attrs["class"] = "form-control"
            #     value.widget.attrs["placeholder"] = value.label
            # else:
            #     value.widget.attrs = {"class": "form-control", "placeholder": f'请输入{value.label}'}
            #

            if value.widget.attrs:
                value.widget.attrs["class"] = f"{old_class} form-control"
                value.widget.attrs["placeholder"] = value.label
            else:
                value.widget.attrs = {"class": f"{old_class} form-control", "placeholder": f'请输入{value.label}'}


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass
