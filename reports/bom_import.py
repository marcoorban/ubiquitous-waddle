from datetime import date
import csv
from .models import Part, BomBike, BikeReport
from .importers import Csv_Importer
from django.core.files.uploadedfile import InMemoryUploadedFile


BAD_BOM_INPUTS = ["MISSING", "INVALID", "NOT FOUND", "NONE"]




class Bom_Importer(Csv_Importer):



    ################## WHY DO I NEED THE BELOW FUNCTIONS?????? ##################

    def create_combos(self, components):
        # Create the combo objects. Combo objects will only be created if its component objects are valid and if the combo using the specified components does not already exist.
        # HBSTEM COMBO CREATION
        # NOTE: If the STEM is NONE, then we have an integrated handlebar stem. The combo for this must be created.
        if (
            components["hb"]["part"].agile_number not in BAD_BOM_INPUTS
            and components["stem"]["part"].agile_number not in ["MISSING", "INVALID", "NOT FOUND"]
        ):
            if not Combo.objects.filter(part1=components["hb"]["part"], part2=components["stem"]["part"]).exists():
                # First production date -> [year, month]
                first_pdate = self.get_fpd(components["hb"]["part"], components["stem"]["part"], "Hbstem")
                combo = Combo.objects.create(part1=components["hb"]["part"], part2=components["stem"]["part"], first_prod_year=first_pdate[0], first_prod_month=first_pdate[1], combo_type="Hbstem")
                combo.save()
        # SDLSTP COMBO CREATION
        if (
            components["saddle"]["part"].agile_number not in BAD_BOM_INPUTS
            and components["sp"]["part"].agile_number not in BAD_BOM_INPUTS
        ):
            if not Combo.objects.filter(part1=components["saddle"]["part"], part2=components["sp"]["part"]).exists():
                # First production date -> [year, month]
                first_pdate = self.get_fpd(components["saddle"]["part"], components["sp"]["part"], "Sdlstp")
                combo = Combo.objects.create(part1=components["saddle"]["part"], part2=components["sp"]["part"], first_prod_year=first_pdate[0], first_prod_month=first_pdate[1], combo_type="Sdlstp")
                combo.save()
        # BBC COMBO CREATION
        # If the BBC is NONE, then we have an combo for Ebike. The combo for this must be created.
        if (
            components["bb"]["part"].agile_number not in ["MISSING", "INVALID", "NOT FOUND"]
            and components["cs"]["part"].agile_number not in BAD_BOM_INPUTS
        ):
            if not Combo.objects.filter(part1=components["bb"]["part"], part2=components["cs"]["part"]).exists():
                # First production date -> [year, month]
                first_pdate = self.get_fpd(components["bb"]["part"], components["cs"]["part"], "BBC")
                combo = Combo.objects.create(part1=components["bb"]["part"], part2=components["cs"]["part"],first_prod_year=first_pdate[0], first_prod_month=first_pdate[1], combo_type="BBC")
                combo.save()


    def get_fpd(self, part1, part2, combo_type):
        """Returns the month and year when a combo was first used in a bike."""
        if combo_type == "Hbstem":
            first_bike = BomBike.objects.filter(handlebar=part1, stem=part2).order_by("production_year", "production_month")[0]
            return [first_bike.production_year, first_bike.production_month]
        elif combo_type == "Sdlstp":
            first_bike = BomBike.objects.filter(saddle=part1, seatpost=part2).order_by("production_year", "production_month")[0]
            return [first_bike.production_year, first_bike.production_month]
        elif combo_type == "BBC":
            first_bike = BomBike.objects.filter(bottom_bracket=part1, crankset=part2).order_by("production_year", "production_month")[0]
            return [first_bike.production_year, first_bike.production_month]

