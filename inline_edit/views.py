from django.views.generic import DetailView, UpdateView
from django.utils.decorators import classonlymethod
from django.core.exceptions import ImproperlyConfigured


def conditional_dispatch(condition_func, true_view, false_view):
	def dispatch(request, *args, **kwargs):
		if condition_func(request, *args, **kwargs):
			return true_view(request, *args, **kwargs)
		else:
			return false_view(request, *args, **kwargs)
	return dispatch

def dict_diff(dict1, dict2):
	try:
		diff_set = set(dict1.iteritems()) - set(dict2.iteritems())
	except TypeError:
		raise TypeError('all properties on subclasses of ConditionalDispatchView must be hashable')
	return dict(diff_set)

class ConditionalDispatchView(object):
	"""
	override this class to set items on both subclasses
	"""
	class Meta:
		pass
	@classonlymethod
	def as_view(cls, condition_func=None, condition_func_factory=None,
		true_view_class=None, false_view_class=None, **initkwargs
	):
		if true_view_class is None:
			try:
				true_view_class = cls.Meta.true_view_class
			except AttributeError:
				raise ImproperlyConfigured(
					"No view to direct to when condition_function returns"
					" True. Either provide a true_view_class, or define a"
					" true_view_class property on this view's Meta class."
				)
		if false_view_class is None:
			try:
				false_view_class = cls.Meta.false_view_class
			except AttributeError:
				raise ImproperlyConfigured(
					"No view to direct to when condition_function returns"
					" False. Either provide a false_view_class, or define a"
					" false_view_class property on this view's Meta class."
				)
		
		# get properties defined on this subclass as base initkwargs
		# we need to walk up the mro, to ensure we get properties of intermediate classes
		base_initkwargs = {}
		for c in reversed(cls.__mro__[:2]):
			base_initkwargs.update(c.__dict__)
		base_initkwargs = dict_diff(base_initkwargs, ConditionalDispatchView.__dict__)
		base_initkwargs.update(initkwargs)
		
		# remove the Meta class; that's for us, not the view class
		base_initkwargs.pop('Meta', None)
		
		# create class-specific keyword arguments
		true_initkwargs = {}
		false_initkwargs = {}
		
		for k, v in base_initkwargs.iteritems():
			if hasattr(true_view_class, k):
				true_initkwargs[k] = v
			if hasattr(false_view_class, k):
				false_initkwargs[k] = v
		
		true_view = true_view_class.as_view(**true_initkwargs)
		false_view = false_view_class.as_view(**false_initkwargs)
		
		if condition_func is None:
			try:
				condition_func = cls.Meta.condition_func
			except AttributeError:
				if condition_func_factory is None:
					try:
						condition_func_factory = cls.Meta.condition_func_factory
					except AttributeError:
						raise ImproperlyConfigured(
							"No condition_func or condition_func_factory has been"
							" defined. Provide one of them, either as a kwarg"
							" to as_view or as a property on this view's Meta class."
						)
				# construct a condition func for this view's model
				try:
					true_queryset = true_view_class(**true_initkwargs).get_queryset()
				except AttributeError:
					true_model = None
				try:
					false_queryset = false_view_class(**false_initkwargs).get_queryset()
				except AttributeError:
					false_model = None
				condition_func = condition_func_factory(true_queryset, false_queryset)
				if not callable(condition_func):
					raise TypeError('condition_func must be callable')
		
		return conditional_dispatch(condition_func, true_view, false_view)

class InlineUpdateView(ConditionalDispatchView):
	template_name_suffix = '_inline_form'
	class Meta:
		true_view_class = UpdateView
		false_view_class = DetailView
		@staticmethod
		def condition_func_factory(true_queryset, false_queryset):
			# default condition_func checks if user 'can_change' the object
			true_model = true_queryset.model
			app_label = true_model._meta.app_label
			change_perm = true_model._meta.get_change_permission()
			def condition_func(request, *args, **kwargs):
				return request.user.has_perm(app_label + '.' + change_perm)
		

