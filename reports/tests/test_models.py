from django.test import TestCase

from ..models import BomBike, MfrPartName, Part, BomBike, TestReportPart, TestReportCombo

class MfrPartNameTests(TestCase):

    def setUp(self):
        mfr1 = MfrPartName.objects.create(name="ICO-12")

    def test_model_creation(self):
        mfr2 = MfrPartName.objects.create(name="ICO-25")
        mfr3 = MfrPartName.objects.create(name="ICO-234")
        self.assertEqual(len(MfrPartName.objects.all()), 3)

    def test_model_str(self):
        mfr = MfrPartName.objects.create(name="ICO-88")
        self.assertEqual(str(mfr), "ICO-88")

    def test_model_not_empty(self):
        mfr_empty = MfrPartName.objects.create(name="")
        self.assertEqual(len(MfrPartName.objects.all()), 1)

class BikeModelTests(TestCase):

    def test_create_bike(self):
        BomBike.objects.create(
            model='Test bike',
            model_year=2023,
            size='M'
        )
        self.assertTrue(len(BomBike.objects.all()) == 1)

    def test_correct_bike_data(self):
        bike = BomBike(
            model='Tarmac',
            model_year=2323,
            size='L'
        )
        self.assertEqual(bike.model, 'Tarmac') 
        self.assertEqual(bike.model_year, 2323)
        self.assertEqual(bike.size, 'L')

class BikeModelMethodTests(TestCase):

    def test_clean_model(self):
        """returns True if all the whitespace has been properly removed."""
        name = "   Bike model without       spaces    "
        bike = BomBike(model=name)
        self.assertEqual(bike.clean_model(), "Bikemodelwithoutspaces")

class PartModelTests(TestCase):

    def test_create_part(self):
        part = Part(
            agile_number="0123456789",
            lifecycle='Preliminary',
            description="This is most definitely a part",
            part_type = 'Frame',
        )
        self.assertEqual(part.agile_number, "0123456789")
        self.assertEqual(part.lifecycle, 'Preliminary')
        self.assertEqual(part.description, 'This is most definitely a part')
        self.assertEqual(part.part_type, 'Frame')

    def test_add_names(self):
        part = Part(
            agile_number="0123456789",
            lifecycle='Preliminary',
            description="This is most definitely a part",
            part_type = 'Frame',
        )
        part.save()
        name1 = MfrPartName(name="part 1")
        name1.save()
        name2 = MfrPartName(name='another name for pt 1')
        name2.save()
        part.names_list.add(name1)
        part.names_list.add(name2)
        self.assertTrue(len(part.names_list.all()) == 2)




