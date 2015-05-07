import unittest
from selenium import webdriver

import clients

GALLERY_URL = 'http://plejada.onet.pl/newsy/modna-scarlett-johansson-na-ulicach-nowego-jorku/qvwfk6'


class SingleGalleryCounterTests(unittest.TestCase):

    def setUp(self):
        super(SingleGalleryCounterTests, self).setUp()
        self.client = clients.PlejadaSingleGalleryClient()

    def test_incrementation_of_counter(self):
        page_numbers = self.client.get_all_page_numbers(GALLERY_URL)
        self.assertEquals([1, 2, 3, 4, 5], page_numbers)

    def test_page_count(self):
        self.assertEquals(5, self.client.get_page_count(GALLERY_URL))


class SeleniumTestCase(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()


class MainGalleryTests(SeleniumTestCase):

    def setUp(self):
        super(MainGalleryTests, self).setUp()
        self.client = clients.PlejadaMainGalleryClient(self.driver)

    def test_image_loading_during_scrolling(self):
        self.client.visit_page()
        start_image_count = self.client.count_gallery_images()
        self.client.scroll_down()
        finish_image_count = self.client.count_gallery_images()
        self.assertLess(start_image_count, finish_image_count)
