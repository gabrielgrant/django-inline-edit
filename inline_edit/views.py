from django.views import View, DetailView, UpdateView
from django.utils.decorators import classonlymethod
from django.models import Permission
from django.core.exceptions import ImproperlyConfigured


def conditional_dispatch(condition_func, true_view, false_view):
	def dispatch(request, *args, **kwargs):
		if condition_func(request, *args, **kwargs):
			return true_view(request, *args, **kwargs)
		else:
			return false_view(request, *args, **kwargs)
	return dispatch

def dict_diff(dict1, dict2):
	diff_set = set(dict1.iteritems()) - set(dict2.iteritems())
	return dict(diff_set)

class ConditionalDispatchView(object):
	"""
	TODO: allow overriding this class, to set items on both subclasses
	"""
	class Meta:
		pass
	@classonlymethod
	def as_view(cls, condition_func=None,
		true_view_class=None, false_view_class=None, **initkwargs
	):
		if true_view_class is None
			try:
				true_view_class = cls.Meta.true_view_class
			except AttributeError:
				raise ImproperlyConfigured(
					"No view to direct to when condition_function returns"
					" True. Either provide a true_view_class, or define a"
					" true_view_class property on this view's Meta class."
				)
		if false_view_class is None
			try:
				false_view_class = cls.Meta.false_view_class
			except AttributeError:
				raise ImproperlyConfigured(
					"No view to direct to when condition_function returns"
					" False. Either provide a false_view_class, or define a"
					" false_view_class property on this view's Meta class."
				)
        
        # get properties defined on this subclass as base initkwargs
        base_initkwargs = dict_diff(cls, ConditionalDispatchView)
        base_initkwargs.update(initkwargs)
        
        # remove the Meta class; that's for us, not the view class
         base_initkwargs.pop('Meta', None)
        
        # create class-specific keyword arguments
		true_initkwargs = {}
		false_initkwargs = {}
        
        for k, v in base_initkwargs.iter_items():
            if hasattr(true_view_class, k):
                true_initkwargs[key] = v
            if hasattr(false_view_class, k):
                false_initkwargs[key] = v
		
		true_view = true_view_class().as_view(**true_initkwargs)
		false_view = false_view_class().as_view(**false_initkwargs)
		
		if condition_func is None:
			# default condition_func checks if user 'can_change' the object
			model = true_view_class(**true_initkwargs).get_queryset().model
			app_label = model._meta.app_label
			change_perm = model._meta.get_change_permission()
			def condition_func(request, *args, **kwargs)
				return request.user.has_perm(app_label + '.' + change_perm)
		
		return conditional_dispatch(condition_func, true_view, false_view)

class InlineUpdateView(ConditionalDispatchView):
	template_name_suffix = '_inline_form'
	class Meta:
		true_view_class = UpdateView
		false_view_class = DetailView


