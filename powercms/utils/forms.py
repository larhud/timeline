# coding:utf-8
# -*- coding: utf-8 -*-
#
# Isnard Aguiar 10/06/2012 - #0001 - classe SpanWidget e comentario da UFChoiceFormField
# Augusto Men (https://github.com/augustomen) and
# Nando Florestan (https://github.com/nandoflorestan) - class DateRangeField
#

from __future__ import absolute_import, division

from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import DateField, MultiValueField
from django.forms.utils import flatatt
from django.forms.widgets import DateInput, HiddenInput, MultiWidget
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class SpanWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''

        if isinstance(value, str):
            value = force_text(value)

        return mark_safe('<span%s>%s</span>\n%s' % (
            flatatt(self.build_attrs(attrs)),
            value,
            HiddenInput().render(name, value)
        ))


# Isnard 10/06/2012 - #0001


class BRDateFormField(forms.DateField):
    def __init__(self, *args, **kwargs):
        super(BRDateFormField, self).__init__(*args, **kwargs)
        self.widget.format = '%d/%m/%Y'
        # Aqui ele irá aceitar a data no formato brasileiro e no formato que o JS do calendário entrega para o campo
        self.input_formats = ['%d/%m/%Y', '%Y-%m-%d']


class BRDecimalFormField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super(BRDecimalFormField, self).__init__(*args, **kwargs)
        self.localize = True
        self.widget.is_localized = True


class DateInput5(DateInput):
    """
    Renders a bootstrap + jquery date input.
    """

    # input_type = "date" isn't yet fully supported except by webkit and opera.
    # also, inputs type date can't have datepicker customized, so we use
    # input type=text and jquery datepicker
    input_type = 'text'

    def render(self, name, value, attrs=None, renderer=None):
        final = {'class': "input-small", 'placeholder': "dia/mês/ano"}
        if attrs:
            final.update(attrs)
        tag = super(DateInput5, self).render(name, value, final)
        return mark_safe(
            '<div class="input-append datepicker">' +
            tag + '''<button class="btn"
            type="button"><i class="icon-calendar"></i></button>
        </div>''')


class DateField5(DateField):
    """
    Represents a date input with bootstrap css and jquery date picker

    TODO: put it in field media
  <script src="{% static "js/jquery-ui/js/jquery-ui-1.8.22.custom.min.js" %}"
    type="text/javascript"></script>
  <script src="{% static "js/jquery-ui/js/jquery.ui.datepicker-pt-BR.js" %}"
    type="text/javascript"></script>

    Need that :)

    """

    def __init__(self, placeholder=None, autofocus=None, **kw):
        self.placeholder = placeholder
        self.autofocus = autofocus
        super(DateField5, self).__init__(**kw)

    def widget_attrs(self, widget):
        attrs = super(DateField5, self).widget_attrs(widget)
        attrs['placeholder'] = self.placeholder
        if self.autofocus:
            attrs['autofocus'] = 'autofocus'
        if self.required:
            attrs['required'] = 'required'
        # TODO: if using type=date, support date ranges, check w3c html5 ref.
        # if self.min_value:
        #     attrs['min'] = self.min_value
        # if self.max_value:
        #     attrs['max'] = self.max_value
        return attrs


class DateRangeInput(MultiWidget):
    """
    Render a filter with start date and end date using bootstrap and jquery.
    """

    def __init__(self, till_today=True, attrs=None):
        """
        The *till_today* flag configures what happens when the second date
        is blank. If true, the application receives today's date; if false,
        a ValidationError is raised. True is the default.
        """
        self.till_today = till_today
        # TODO: i18n
        end = dict(title='Se em branco, é considerada a data de hoje.') \
            if till_today else None
        widget = (DateInput5(), DateInput5(attrs=end),)
        super(DateRangeInput, self).__init__(widget, attrs=attrs)

    def decompress(self, value):
        """
        Called when rendering the widget.
        """
        return value or (None, None)

    def format_output(self, rendered_widgets):
        return mark_safe('\n&nbsp; a &nbsp;\n'.join(rendered_widgets))


class DateRangeField(MultiValueField):
    """ Represents a filter with start date and end date. """
    widget = DateRangeInput

    def __init__(self, input_formats=None, **kwargs):
        localize = kwargs.get('localize', False)
        fields = (
            DateField5(input_formats=input_formats,
                       localize=localize,
                       **kwargs),
            DateField5(input_formats=input_formats,
                       localize=localize,
                       **kwargs)
        )
        super(DateRangeField, self).__init__(fields, **kwargs)

    def compress(self, data_list):
        """
        Gets and returns something like [None, datetime.date(2012, 8, 1)].

        Checks that either both values are present, or none.
        Also ensures the values make sense in relation to each other.
        """
        if not data_list or (not data_list[0] and not data_list[1]):
            return None, None
        elif not data_list[0]:
            # TODO: i18n
            raise ValidationError('Falta preencher a data inicial.')
        elif not data_list[1]:
            if hasattr(self.widget, 'till_today') and self.widget.till_today:
                data_list[1] = date.today()
            else:
                # TODO: i18n
                raise ValidationError('Falta preencher a data final.')
        elif data_list[0] > data_list[1]:
            # TODO: i18n
            raise ValidationError('A data inicial está posterior à final.')
        return data_list
