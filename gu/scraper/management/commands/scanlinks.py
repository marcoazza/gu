from django.core.management import BaseCommand
# from multiprocessing import Pool
import requests
from scraper.models import Category, Type, Publisher, CompetitionNotice
# from django.utils import timezone
from scraper.utils import sitescraper

PROCESSPOOLSIZE = 10
# VALID_STATUS = { i[0] for i in OffendingItem.OI_STATUS_CHOICES}


# def evaluate_page(url):
#     """Evaluate if input url is valid or not.

#     A url is considered valid if its response status
#     is 200, and considered invalid its status code is
#     404 or it contains the string `copyright compliant`
#     in its response content.

#     Args:
#         url: url to analyze

#     Returns:
#         status code for a valid page (200) or an invalid
#         page (400), `None` otherwise.
#     """
#     try:
#         response = requests.get(url)
#         status = response.status_code
#         #if status is not a known status, skip url
#         if not status in VALID_STATUS:
#             return OffendingItem.STATUS_UNKNOWN
#         if status == OffendingItem.STATUS_LIVE and \
#            "copyright complaint" in response.text:
#                 status = OffendingItem.STATUS_DEAD
#         return status
#     except requests.exceptions.RequestException:
#         return None


def _store_url(item):
    """Store a new url element into database.

    Based on `product` it stores new url element.
    If the url already exist, it updates its status
    and it `date_found` field, otherwise the function
    creates a new `OffendingItem` element.

    Args:
        url: url to store

        code: associated code found in response

        product: product associated with url
    """
    # try:
    comp, status = Category.objects.get_or_create(name=item.category)
    comp_type, status = Type.objects.get_or_create(name=item.comp_type)
    publisher, status = Publisher.objects.get_or_create(name=item.publisher)

    #with manula defined primary keys get_or_create() has same behavior
    #of create(), so it will raise IntegrityError if item already exists
    try:
        obj = CompetitionNotice.objects.get(code=item.code)
    except CompetitionNotice.DoesNotExist:
        obj = CompetitionNotice.objects.create(code=item.code,
            header=item.header, url=item.url, pub_date=item.pub_date,
            comp_type=comp_type, comp_date=item.expiry_date,category=comp,
            publisher=publisher)
        obj.save()
    # except Product.DoesNotExist:
    #     prod = Product.objects.create(title=product)
    #     prod.save()

    # try:
    #     off_item = OffendingItem.objects.get(url=url)
    #     off_item.status = code
    #     off_item.date_found = timezone.now()
    #     off_item.save()
    # except OffendingItem.DoesNotExist:
    #     OffendingItem.objects.create(url=url,
    #                                  status=code,
    #                                  date_found=timezone.now(),
    #                                  product_id=prod.id)


def get_page(url):
    try:
        out = sitescraper.parse(url)
        return out
    except requests.exceptions.RequestException:
        # print('RequestException')
        return None
    except sitescraper.ScrapingError:
        # print('Scraper Broken')
        return None



class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('urls', nargs='*', type=str)

        # # Named (optional) arguments
        parser.add_argument(
            '--file',
            action='store',
            dest='file',
            help='Load URLs from file',
        )

    def handle(self, *args, **options):
        """Handle command behaviour.

        `scanlinks` command evaluates one or more urls
        and determine its status using the following rules:
            -if the page returns http status 404 then it's dead
            -if the page returns http status 200 then it's live
            -if the page HTML contains the text `copyright complaint`
             it is dead

        If a url is in an invalid status, or unknown, `status` value
        is set to `None` and the database
        Args:
            urls: a list of urls to test

            file: a file to use as url source
        """
        offending_links = []
        product = 'default'
        if not options['urls'] and not options['file']:
            self.stdout.write(self.style.SUCCESS('Nothing to parse!'))
            return

        for url in options['urls']:
            offending_links.append(url)

        if options['file']:
            try:
                with open(options['file'], 'r') as url_file:
                    offending_links = url_file.readlines()
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('Invalid URLs file'))
                return

        for i in offending_links:
            res = get_page(i)
            if not res:
                self.stdout.write(self.style.ERROR('Invalid URL:  {}'.format(i)))
            else:
                print(res)
                for i in res:
                    print('store')
                    _store_url(i)
        # with Pool(processes=PROCESSPOOLSIZE) as pool:
        #     res = pool.map(get_page, offending_links)
        #     # print('Res:   ',res)
        #     for url_idx, code in enumerate(res):
        #         if code is None:
        #             self.stdout.write(self.style.ERROR('Invalid URL:  {}'.format(offending_links[url_idx])))
        #         else:
        #             print('store')
        #             # _store_url(offending_links[url_idx], code, product)

        self.stdout.write(self.style.SUCCESS('Successfully parsed URLs'))
