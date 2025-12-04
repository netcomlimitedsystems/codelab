from django import template

register = template.Library()

@register.simple_tag
def query_string(param, value, request):
    """
    Builds a query string for pagination and sorting while preserving existing filters
    """
    query_dict = request.GET.copy()
    
    if param == 'page':
        # For pagination, just update the page number
        query_dict[param] = value
    else:
        # For other parameters, update or add the parameter
        if value:
            query_dict[param] = value
        else:
            # Remove the parameter if value is empty
            if param in query_dict:
                del query_dict[param]
    
    # Remove page parameter when changing other filters (to go back to page 1)
    if param != 'page':
        if 'page' in query_dict:
            del query_dict['page']
    
    return query_dict.urlencode()