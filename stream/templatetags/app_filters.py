from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='to_length')
def to_length(value):
	value = int(value)
	h = value // 3600
	m = (value % 3600) // 60
	s = (value % 3600) % 60

	out = ""
	if h > 0:
		out += str(h) + ":"
	
	if m < 10 and h > 0:
		out += "0"

	out += str(m) + ":"

	if s < 10:
		out += "0"
	
	return out + str(s)

@register.filter(name="to_image")
def to_image(value, arg):
	return "/image/%s/%d/%s/" % (value.__class__.__name__.lower(), value.id, arg)

@register.filter(name="playcount")
def playcount(value):
	return mark_safe('<span class="playcount" data-ps-model="%s" data-ps-id="%d">%d</span>' % (value.__class__.__name__.lower(), value.id, value.playcount))

@register.filter(name="de_the")
def de_the(value):
	if value[:4].lower() == "the ": return value[4:]
	else: return value
