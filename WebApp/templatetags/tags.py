import re

from django.template import Library, TemplateSyntaxError
from django.template.defaulttags import ForNode
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

register = Library()


@register.tag('cfor')
def do_conditional_for(parser, token):
    """
    Loops over each item in an array.
    ========================== ================================================
    Variable Description
    ========================== ================================================
    ``forloop.counter`` The current iteration of the loop (1-indexed)
    ``forloop.counter0`` The current iteration of the loop (0-indexed)
    ``forloop.revcounter`` The number of iterations from the end of the
    loop (1-indexed)
    ``forloop.revcounter0`` The number of iterations from the end of the
    loop (0-indexed)
    ``forloop.first`` True if this is the first time through the loop
    ``forloop.last`` True if this is the last time through the loop
    ``forloop.parentloop`` For nested loops, this is the loop "above" the
    current one
    ========================== ================================================
    """
    bits = token.split_contents()
    if len(bits) < 8:
        raise TemplateSyntaxError("'cfor' statements should have at least eight"
            " words: %s" % token.contents)
    is_reversed = bits[-1] == 'reversed'
    in_index = -7 if is_reversed else -6
    if_index = -5 if is_reversed else -4
    else_index = -3 if is_reversed else -2
    if bits[in_index] != 'in':
        raise TemplateSyntaxError("'cfor' statements should use the format"
            " 'cfor x in y if z else k': %s" % token.contents)
    loopvars = re.split(r' *, *', ' '.join(bits[1:in_index]))
    for var in loopvars:
        if not var or ' ' in var:
            raise TemplateSyntaxError("'cfor' tag received an invalid argument:"
                " %s" % token.contents)
    condition = parser.compile_filter(bits[if_index + 1])
    consequence = parser.compile_filter(bits[else_index + 1])
    sequence = parser.compile_filter(bits[in_index + 1])
    nodelist_loop = parser.parse(('empty', 'endcfor',))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endcfor',))
        parser.delete_first_token()
    else:
        nodelist_empty = None
    return cForNode(loopvars, sequence, is_reversed, nodelist_loop, condition, consequence, nodelist_empty)


class cForNode(ForNode):
    def __init__(self, loopvars, sequence, is_reversed, nodelist_loop, condition, consequence, 
            nodelist_empty=None):
        super(cForNode, self).__init__(loopvars, sequence, is_reversed, nodelist_loop, nodelist_empty)
        self.condition, self.consequence = condition, consequence

    def render(self, context):
        if 'forloop' in context:
            parentloop = context['forloop']
        else:
            parentloop = {}
        with context.push():
            try:
                condition = self.condition.resolve(context, True)
                if condition:
                    values = self.sequence.resolve(context, True)
                else:
                    values = self.consequence.resolve(context, True)
            except VariableDoesNotExist:
                values = []
            if values is None:
                values = []
            if not hasattr(values, '__len__'):
                values = list(values)
            len_values = len(values)
            if len_values < 1:
                return self.nodelist_empty.render(context)
            nodelist = []
            if self.is_reversed:
                values = reversed(values)
            num_loopvars = len(self.loopvars)
            unpack = num_loopvars > 1
            # Create a forloop value in the context. We'll update counters on each
            # iteration just below.
            loop_dict = context['forloop'] = {'parentloop': parentloop}
            for i, item in enumerate(values):
                # Shortcuts for current loop iteration number.
                loop_dict['counter0'] = i
                loop_dict['counter'] = i + 1
                # Reverse counter iteration numbers.
                loop_dict['revcounter'] = len_values - i
                loop_dict['revcounter0'] = len_values - i - 1
                # Boolean values designating first and last times through loop.
                loop_dict['first'] = (i == 0)
                loop_dict['last'] = (i == len_values - 1)
                pop_context = False
                if unpack:
                    # If there are multiple loop variables, unpack the item into
                    # them.
                    # To complete this deprecation, remove from here to the
                    # try/except block as well as the try/except itself,
                    # leaving `unpacked_vars = ...` and the "else" statements.
                    if not isinstance(item, (list, tuple)):
                        len_item = 1
                    else:
                        len_item = len(item)
                    # Check loop variable count before unpacking
                    if num_loopvars != len_item:
                        warnings.warn(
                            "Need {} values to unpack in for loop; got {}. "
                            "This will raise an exception in Django 2.0."
                            .format(num_loopvars, len_item),
                            RemovedInDjango20Warning)
                    try:
                        unpacked_vars = dict(zip(self.loopvars, item))
                    except TypeError:
                        pass
                    else:
                        pop_context = True
                        context.update(unpacked_vars)
                else:
                    context[self.loopvars[0]] = item
                # In debug mode provide the source of the node which raised
                # the exception
                # print type(context)
                # if context.template.engine.debug:
                #     for node in self.nodelist_loop:
                #         try:
                #             nodelist.append(node.render(context))
                #         except Exception as e:
                #             if not hasattr(e, 'django_template_source'):
                #                 e.django_template_source = node.source
                #                 raise
                # else:
                for node in self.nodelist_loop:
                    nodelist.append(node.render(context))
                if pop_context:
                    # The loop variables were pushed on to the context so pop them
                    # off again. This is necessary because the tag lets the length
                    # of loopvars differ to the length of each set of items and we
                    # don't want to leave any vars from the previous loop on the
                    # context.
                    context.pop()
        return mark_safe(''.join(force_text(n) for n in nodelist))