import unittest

from scripts.extract_customer_catalog_photos import match_rows


class SourcePhotoRowsTest(unittest.TestCase):
    def test_rejects_code_hidden_under_page_header(self):
        words = [dict(text="ABC01-2", x0=12, x1=43, top=27)]
        pic = dict(name="Image1", x0=51, x1=143, top=60, bottom=140)
        self.assertEqual(match_rows(words, [pic], {"ABC01-2"}, 842), [])

    def test_matches_exact_code_and_one_complete_picture_inside_its_row(self):
        words = [dict(text="ABC01-2", x0=12, x1=43, top=100),
                 dict(text="DEF02-3", x0=12, x1=43, top=220)]
        pictures = [dict(name="Image1", x0=51, x1=143, top=120, bottom=200)]
        self.assertEqual(match_rows(words, pictures, {"ABC01-2"}, 842),
                         [{"code": "ABC01-2", "image_name": "Image1", "row_top": 100, "row_bottom": 220}])

    def test_rejects_price_column_near_code_and_cross_row_picture(self):
        words = [dict(text="ABC01-2", x0=12, x1=43, top=100),
                 dict(text="DEF02-3", x0=12, x1=43, top=220),
                 dict(text="445", x0=540, x1=570, top=250)]
        pictures = [dict(name="Image1", x0=51, x1=143, top=120, bottom=240)]
        self.assertEqual(match_rows(words, pictures, {"ABC01-2", "ABC01", "445"}, 842), [])

    def test_rejects_ambiguous_images_and_partial_page_rows(self):
        words = [dict(text="ABC01-2", x0=12, x1=43, top=100)]
        pic = dict(name="Image1", x0=51, x1=143, top=120, bottom=200)
        self.assertEqual(match_rows(words, [pic, {**pic, "name": "Image2"}], {"ABC01-2"}, 842), [])
        self.assertEqual(match_rows(words, [{**pic, "bottom": 900}], {"ABC01-2"}, 842), [])

    def test_unmatched_code_still_bounds_the_previous_row(self):
        words = [dict(text="ABC01-2", x0=12, x1=43, top=100),
                 dict(text="UNKNOWN01", x0=12, x1=43, top=220)]
        pic = dict(name="Image1", x0=51, x1=143, top=230, bottom=300)
        self.assertEqual(match_rows(words, [pic], {"ABC01-2"}, 842), [])


if __name__ == "__main__":
    unittest.main()
