# django mongogeneric

Class based generic views for mongoengine documents.

## Note

Not all views Django provides are implemented. If you find mixins or views that are 
missing, feel free to implement them and provide a pull request :-)

## Requirements

  * Django >= 1.3
  * [mongoengine](http://mongoengine.org/) >= 0.6
  * [django-mongodbforms](https://github.com/jschrewe/django-mongodbforms)

## Implemented views

 * DetailView
 * ListView
 * CreateView
 * UpdateView
 * DeleteView

Most of the mixins provided by Django to build the above views are also there.

The Django documentation for 
[class based generic views](https://docs.djangoproject.com/en/dev/ref/class-based-views/)
should work for the views provided here. The only difference is that everywhere
Django requires **model** as an attribute, mongogeneric requires a **document**.

### Embedded forms

Additionally to the above views, there is a view and a mixin that makes
working with embedded document forms easier (e.g. for comments saved together with 
a post).

#### EmbeddedFormMixin

**Extends**: `FormMixin`

A mixin class that processes embedded forms, using `EmbeddedDocumentForm`s from [django mongodbforms](https://github.com/jschrewe/django-mongodbforms).

**embedded\_form\_class**<br />
An `EmbeddedDocumentForm` that is passed into the template context and 
saved if the request is a POST request and the form is valid.

**embedded\_context\_name**<br />
Designates the name of the variable to use in the context.

#### EmbeddedDetailView

**Extends**: `BaseEmbeddedFormMixin`, `DetailView`

Renders a single document and provides a form for an embedded field.


