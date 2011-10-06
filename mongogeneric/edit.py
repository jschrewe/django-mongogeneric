from django.forms import models as model_forms
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, View

from django.views.generic.edit import FormMixin

from mongogeneric.detail import (SingleDocumentMixin, DetailView, 
                                 SingleDocumentTemplateResponseMixin, BaseDetailView)

class DocumentFormMixin(FormMixin, SingleDocumentMixin):
    """
    A mixin that provides a way to show and handle a documentform in a request.
    """

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            if self.document is not None:
                # If a model has been explicitly provided, use it
                document = self.document
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                document = self.get_queryset().model
            return model_forms.modelform_factory(model)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(DocumentFormMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        self.object = form.save()
        return super(DocumentFormMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = kwargs
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        return context
    

class EmbeddedFormMixin(FormMixin):
    """
    A mixin that provides a way to show and handle a documentform in a request.
    """
    embedded_form_class = None
    embedded_context_name = 'embedded_form'

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.embedded_form_class:
            return self.embedded_form_class
        else:
            raise ImproperlyConfigured(
                    "No embedded form class provided. An embedded form class must be provided.")

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        object = getattr(self, 'object', self.get_object())
        return form_class(object, **self.get_form_kwargs())
    
    def get_embedded_object(self):
        """
        Returns an instance of the embedded object. By default this is a freshly created
        instance. Override for something cooler.
        """
        if hasattr(self, 'embedded_object'):
            return self.embedded_object()
        else:
            klass = self.get_form_class()
            return klass.Meta.document()

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(EmbeddedFormMixin, self).get_form_kwargs()
        object = self.get_embedded_object()
        kwargs.update({'instance': object})
        if not 'initial' in kwargs:
            kwargs['initial'] = {}
        return kwargs

    def get_success_url(self):
        object = getattr(self, 'object', self.get_object())
        if self.success_url:
            url = self.success_url % object.__dict__
        else:
            try:
                url = object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        self.embedded_object = form.save()
        return super(EmbeddedFormMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EmbeddedFormMixin, self).get_context_data(**kwargs)
        
        object = getattr(self, 'object', self.get_object())
        if 'form' in kwargs:
            form = kwargs['form']
        else:
            form = self.get_form(self.get_form_class())
        context[self.embedded_context_name] = form
        
        return context

class ProcessEmbeddedFormMixin(object):
    """
    A mixin that processes an embedded form on POST. 
    Does not implement any GET handling.
    """
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        super(ProcessEmbeddedFormMixin, self).post(request, *args, **kwargs)

class BaseEmbeddedFormMixin(EmbeddedFormMixin, ProcessEmbeddedFormMixin):  
    """
    A Mixin that handles an embedded form on POST and 
    adds the form into the template context.
    """      

class ProcessFormView(View):
    """
    A mixin that processes a form on POST.
    """
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormView(FormMixin, ProcessFormView):
    """
    A base view for displaying a form
    """


class FormView(TemplateResponseMixin, BaseFormView):
    """
    A view for displaying a form, and rendering a template response.
    """


class BaseCreateView(DocumentFormMixin, ProcessFormView):
    """
    Base view for creating an new object instance.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).post(request, *args, **kwargs)


class CreateView(SingleDocumentTemplateResponseMixin, BaseCreateView):
    """
    View for creating an new object instance,
    with a response rendered by template.
    """
    template_name_suffix = '_form'


class BaseUpdateView(DocumentFormMixin, ProcessFormView):
    """
    Base view for updating an existing object.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class UpdateView(SingleDocumentTemplateResponseMixin, BaseUpdateView):
    """
    View for updating an object,
    with a response rendered by template..
    """
    template_name_suffix = '_form'


class DeletionMixin(object):
    """
    A mixin providing the ability to delete objects
    """
    success_url = None

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    # Add support for browsers which only accept GET and POST for now.
    def post(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")


class BaseDeleteView(DeletionMixin, BaseDetailView):
    """
    Base view for deleting an object.

    Using this base class requires subclassing to provide a response mixin.
    """


class DeleteView(SingleDocumentTemplateResponseMixin, BaseDeleteView):
    """
    View for deleting an object retrieved with `self.get_object()`,
    with a response rendered by template.
    """
    template_name_suffix = '_confirm_delete'

class EmbeddedDetailView(BaseEmbeddedFormMixin, DetailView):
    """
    Renders the detail view of a document and and adds a
    form for an embedded object into the template.
    
    See BaseEmbeddedFormMixin for details on the form.
    """
    def get_context_data(self, **kwargs):
        # manually call parents get_context_data without super
        # currently django messes up the super mro chain
        # and for multiple inheritance only one tree is followed
        context = BaseEmbeddedFormMixin.get_context_data(self, **kwargs)
        context.update(DetailView.get_context_data(self, **kwargs))
        return context
