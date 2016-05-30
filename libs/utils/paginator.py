import collections
from math import ceil
from django.utils import six


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class Paginator(object):
    def __init__(self, url, total, per_page, per_page_param='perPage', page_param='page',
        orphans=0, allow_empty_first_page=True):
        self.url = url
        self.per_page_param = per_page_param
        self.page_param = page_param
        self.per_page = int(per_page)
        self.count = total
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages = None


    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number


    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(number, self)


    def _get_page(self, *args, **kwargs):
        """
        Returns an instance of a single page.
        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)


    def _get_num_pages(self):
        """
        Returns the total number of pages.
        """
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.orphans)
                self._num_pages = int(ceil(hits / float(self.per_page)))
        return self._num_pages
    num_pages = property(_get_num_pages)


    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return list(six.moves.range(1, self.num_pages + 1))

    page_range = property(_get_page_range)


class Page(object):
    def __init__(self, number, paginator):
        self.number = number
        self.paginator = paginator


    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)


    def has_next(self):
        return self.number < self.paginator.num_pages


    def has_previous(self):
        return self.number > 1


    def has_other_pages(self):
        return self.has_previous() or self.has_next()


    def is_not_empty(self):
        return self.paginator.num_pages


    def next_page(self):
        num = self.paginator.validate_number(self.number + 1)
        return {
            'link': "%s&%s=%d" % (self.__form_url(), self.paginator.page_param, num), 
            'num': num
        }


    def previous_page(self):
        num = self.paginator.validate_number(self.number - 1)
        return {
            'link': "%s&%s=%d" % (self.__form_url(), self.paginator.page_param, num), 
            'num': num
        }


    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1


    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page

    def __form_url(self):
        from urlparse import urlparse, parse_qs
        from urllib import urlencode
        pg = self.paginator
        parsedUrl = urlparse(pg.url)
        query_params = parse_qs(parsedUrl.query)
        query_params[pg.per_page_param] = pg.per_page
        query_params.pop(pg.page_param, None)
        return parsedUrl.path + '?' + urlencode(query_params, doseq=True)


    def indented(self, total):        
        left = (total - 1) // 2
        right = total - left - 1
        pg = self.paginator
        page_num = pg.num_pages

        if self.number > left:
            if self.number + right < page_num:
                start = self.number - left
                end = self.number + right
            else:
                start = page_num - total + 1 if page_num - total + 1 > 0 else 1
                end = page_num
        else:
            start = 1
            end = page_num if total > page_num else total
    
        page_range = list(six.moves.range(start, end + 1))
        return [("%s&%s=%d" % (self.__form_url(), pg.page_param, i), i) for i in page_range]