import csv
from datetime import date
from math import prod
from .const import HEADER_DICT, MONTH_DICT
from .models import BikeReport, Part, MfrPartName, TestReportCombo, TestReportPart, BomBike
from .models import SbcProject
from django.core.files.uploadedfile import InMemoryUploadedFile

class Csv_Importer():

    # uploaded_file is of type InMemoryUploadedFile
    def __init__(self, uploaded_file):
        self.file = uploaded_file
        self.is_uploaded_file = isinstance(uploaded_file, InMemoryUploadedFile)
        self.reader = None
        self.csv_type = ""

    def is_csv(self):
        """Determines if the file is csv format by looking at the file extension"""
        # file is a django file wrapper object, and the name is contained in the filename attribute.
        if self.is_uploaded_file:
            return self.file.name.split(".")[-1] == 'csv'
        # Otherwise it's just a path (coming from test suite)
        else:
            return self.file.split(".")[-1] == 'csv'

    def read_file(self):
        """Creates dictionaries from the contesnts of the file using the first row as the header"""
        # This will run if self.file is an uploaded file from browser
        if self.is_uploaded_file:
            contents = self.file.read().decode(errors='ignore').splitlines()
        # This is only for testing purposes (file is read from disk)
        else:
            filecopy = self.file
            with open(filecopy, 'r', newline='', errors='ignore') as f:
                contents = f.read().splitlines()
        try:
            self.reader = csv.DictReader(contents)
            return True
        except:
            return False

    def determine_type(self):
        """Determines if the file uploaded is TRP, TRC, Part, BOM etc by looking at what the header looks like"""
        header = ","
        header = header.join(self.reader.fieldnames)
        for key in HEADER_DICT:
            if header == HEADER_DICT[key]:
                self.csv_type = key
                return
        self.csv_type = "unknown"
        return

    def import_all(self):
        if self.csv_type == 'bom':
            for row in self.reader:
                self.bom_import_line(row)
        for row in self.reader:
            self.import_line(row)

    def import_line(self, row):
        """Import the information from the current row. We ignore any agile numbers that have non digit chars."""
        if not row['Number'].isdigit():
            return False
        if self.csv_type == 'parts':
            is_imported = self.import_part(row)
        elif self.csv_type == 'trp':
            is_imported = self.import_trp(row)
        elif self.csv_type == "trc":
            is_imported = self.import_trc(row)
        elif self.csv_type == "bike_report_info":
            is_imported = self.import_bike_report_info(row)
        elif self.csv_type == "bike_report_toc":
            is_imported = self.import_bike_report_toc(row)
        elif self.csv_type == "sbc_project_search":
            is_imported = self.import_sbcproject(row)
        return is_imported

    def import_part(self, row):
        part_type = row['Part Type']
        if part_type == "Engineered Assembly":
            part_type = self.get_correct_part_type(row['Description'])
        (part, created) = Part.objects.update_or_create(
            agile_number = self.add_zeroes(row['Number']),
            defaults = {
                'description':self.remove_non_ascii(row['Description']),
                'lifecycle':row['Lifecycle Phase'],
                'part_type':part_type
            }
        )
        mfp_part_name = row['Mfr. Part Number (Manufacturers)']
        if mfp_part_name:
            part.names_list.add(MfrPartName.objects.get_or_create(name=mfp_part_name)[0])

    def get_correct_part_type(self, parttype):
        if "FRK" in parttype:
            return 'Fork'
        elif "FRM" in parttype:
            return 'Frame'
        elif "HDLBR" in parttype:
            return 'Handlebars'
        elif "IBS" in parttype:
            return "Handlebars"
        elif "SP TLA" in parttype:
            return "Seat Post"
        elif "STEM" in parttype:
            return "Stem"
        else:
            return "Unknown"
 
    def import_trp(self, row):
        """ TEST REPORT PART """
        # We want to create or update only if the trp document in agile actually has contents (ignore empty TRPs)
        if not row['Item Number (TOC)']:
            return False
        else:
            (trp, created) = TestReportPart.objects.update_or_create(
                agile_number = self.add_zeroes(row['Number']),
                defaults = {
                    'description':self.remove_non_ascii(row['Description']),
                    'lifecycle':row['Lifecycle Phase'],
                    'report_type':row['Test Report Type (Page Three)'],
                    'created_date':self.convert_to_date(row['Create Date (Page Two)']),
                    'manufacturer':row['Base Part Manufacturer (Page Three)']
                }
            )
            # Get the part object. If there isn't one, create a new one
            (part, created) = Part.objects.get_or_create(
                agile_number = self.add_zeroes(row['Item Number (TOC)']),
                defaults = {
                    'description':self.remove_non_ascii(row['Item Description (TOC)']),
                    'lifecycle': row['Item Lifecycle Phase (TOC)'],
                    'part_type':row['Item Type (TOC)']
                }
            )
            # Notify the user if a new part has just been created
            if created:
                print(f"{part} just created!")
            # Add the part to the contents of trp
            trp.part.add(part)

    def import_trc(self, row):
        """ TEST REPORT COMBO """
        # We want to create or update only if the trp document in agile actually has contents (ignore empty TRCs)
        if not row['Item Number (TOC)']:
            return False
        else:
            (trc, created) = TestReportCombo.objects.update_or_create(
                agile_number = self.add_zeroes(row['Number']),
                defaults = {
                    'description':self.remove_non_ascii(row['Description']),
                    'lifecycle': row['Lifecycle Phase'],
                    'report_type':row['Test Report Type (Page Three)'],
                    'created_date':self.convert_to_date(row['Create Date (Page Two)']),
                }
            )
            # Determine the type of the contents of the TRP:
            content_type = row["Item Type (TOC)"]
            # Get the part from the database
            if content_type == "Test Report Part":
                # Get the TRP. If one does not exist, then create one.
                (trp, created) = TestReportPart.objects.get_or_create(
                    agile_number = self.add_zeroes(row['Item Number (TOC)']),
                    defaults = {
                        'description':self.remove_non_ascii(row['Item Description (TOC)']),
                        'lifecycle':row['Item Lifecycle Phase (TOC)']
                    }
                )
                # Notify the user if a new trp was just created
                if created:
                    print(f"{trp} just created!")
                # Add the trp to the trp field of the trc object
                trc.trp.add(trp)
            elif content_type in ["Saddle", "Bottom Bracket", "Crank Set"]:
                # Get the part. If one does not exist, create one.
                (part, created) = Part.objects.get_or_create(
                    agile_number = self.add_zeroes(row['Item Number (TOC)']),
                    defaults = {
                        'description':self.remove_non_ascii(row['Item Description (TOC)']),
                        'lifecycle':row['Item Lifecycle Phase (TOC)'],
                        'part_type':content_type
                    }
                )
                # Notify the user if a new part was just created
                if created:
                    print(f"{part} just created!")
                # Add the part to the part field of the trc object
                trc.part.add(part)
            else:
                print("Unknown TOC Item type")
                return False
        return True

    def import_bike_report_info(self, row):
        
        # Get rid of lines that don't have a pid, or lines that don't have a first prod date
        pid = row["MPL Product ID (Don't Modify) (Page Three)"]
        first_prod_year = row["First Production Year (Page Three)"]
        first_prod_month = row["First Production Month (Page Three)"]
        if not pid or not first_prod_year or not first_prod_month:
            return False

        # Create production date
        first_prod_date = self.parse_date(first_prod_year, first_prod_month)

        # Get other info
        has_attachment = row["Has Attachment (Attachments)"] == "Yes"
        agile_number = row["Number"]
        description = row["Description"]

        # Determine if it's ebike
        ebike = self.is_ebike(description)

        BikeReport.objects.update_or_create(
            agile_number=agile_number,
            defaults = {
                "pid":pid,
                "description":description,
                "first_prod_date":first_prod_date,
                "has_attachment":has_attachment,
                "ebike":ebike,
            }
        )

        return True

    def parse_date(self, year, month):
        months = {
            "Jan":1,
            "Feb":2,
            "Mar":3,
            "Apr":4,
            "May":5,
            "Jun":6,
            "Jul":7,
            "Aug":8, 
            "Sep":9,
            "Oct":10,
            "Nov":11,
            "Dec":12
        }
        year = int(year)
        return date(year, months[month], 1)

    def is_ebike(self, description):
        ebikes = [
            "LEVO", "KENEVO", "TERO", "CREO", "COMO", "VADO", "CHOP", "GLOBE", "HAUL", "VERTO", "MERO"
        ]
        for bike in ebikes:
            if bike in description:
                return True
        return False
        

    def import_bike_report_toc(self, row):
        # Skip any lines that have empty tocs.
        content_agile = row['Item Number (TOC)']
        if not content_agile:
            return False
        
        # Determine if TOC content is TRP or TRC and retrieve item
        item_type = row["Item Type (TOC)"]
        if item_type == "Test Report Combo":
            contents = TestReportCombo.objects.get_or_create(agile_number=content_agile)[0]
        elif item_type == "Test Report Part":
            contents = TestReportPart.objects.get_or_create(agile_number=content_agile)[0]
        else:
            return False

        # Retrieve the Bike report
        (bike_report, created) = BikeReport.objects.get_or_create(
            agile_number=row["Number"], 
            defaults = {
                'description':row["Description"]
            }
        )

        # Add TRP/TRC to Bike report TOC
        if item_type == "Test Report Combo":
            bike_report.trc_list.add(contents)
        elif item_type == "Test Report Part":
            bike_report.trp_list.add(contents)
        return True      
        
    def log_error(self):
        pass

    def remove_non_ascii(self, string):
        """Removes non-ascii characters from the lines since we can't encode those into the database."""
        # converts to ascii
        string = string.encode('ascii', errors='ignore')
        return string.decode()

    def add_zeroes(self, number):
        """Makes sures that the agile numbers are 10 digit numbers with leading zeroes."""
        return number.zfill(10)

    def convert_to_date(self, date_string):
        # date string is of the following format: m/d/y time
        s = date_string.split(" ")
        s = s[0].split("/")
        year = int(s[2])
        month = int(s[0])
        day = int(s[1])
        return date(year, month, day)

    def bom_import_line(self, row):
        # Before we actually create or update bike models with the information
        # inside the bom, we need to make sure that the info is valid
        # This function checks all the agile part number of each components
        # and returns their respective objects from the database.
        # If the info in the bom is invalid, then it will return 
        # placeholders that are also found in the database (missing, invalid, 
        # or none).}
        frame = self.get_part(row["FRAME"], row["FRAME_M"])
        fork = self.get_part(row["FORK"], row["FORK_M"])
        handlebar = self.get_part(row["HB"], row["HB_M"])
        stem = self.get_part(row["STEM"], row["STEM_M"])
        seatpost = self.get_part(row["SP"], row["SP_M"])
        saddle = self.get_part(row["SADDLE"], row["SADDLE_M"])
        bb = self.get_part(row["BB"], row["BB_M"])
        cs = self.get_part(row["CS"], row["CS_M"])

        # We also need the model and the size
        model = row["MODEL"]
        size = row["SIZE"]

        # Get the corresponding bike report by looking up the pid. If there isn't one, create a new one
        report, created = BikeReport.objects.get_or_create(pid=row["PID"])

        # We also need to create a date object from the info
        # In the csv file the date is month-year (e.g. APR-23)
        month = MONTH_DICT[row["PRODUCTION"].split("-")[0]]
        year = 2000 + int(row["PRODUCTION"].split("-")[1])
        production_date = date(year, month, 1)

        BomBike.objects.update_or_create(
            report=report,
            size=size,
            defaults={
                "model": model,
                "frame": frame,
                "fork": fork,
                "handlebar": handlebar,
                "stem": stem,
                "seatpost": seatpost,
                "saddle": saddle,
                "bb": bb,
                "cs": cs,
                "production_date": production_date
            },
        )

    def get_part(self, bom_number, manu):
        """ Returns the part object from the database, using the bom_number
        and the manufacturer info from the csv file to determine if the entry is actually valid or not. There are three placeholder objects that must be initialized into the database from the beginning, MISSING, INVALID and NONE.
        MISSING just means that the csv file should include the part number but for some reason or other it's not there. An actual part goes on the bike, but it's missing in the BOM.
        INVALID means that the info included in the BOM is incorrect, maybe it containts a type or something.
        NONE means that the bike should not include a part of that type, for example for framesets that won't be handlebars or for ebikes there won't be any bottom bracket.
        If the part number is valid but doesn't exist in the database then this function will just create one a return it.
        """

        # If there is a manufacturer but there is no bom number, i.e. cell is empty, then return MISSING.
        if manu and bom_number in (None, ""):
            return Part.objects.get(description="MISSING")
        # If there is a manufacturer and there are non numeric characters in bom number, then return INVALID
        if manu and not bom_number.isdigit():
            return Part.objects.get(description="INVALID")
        # If there is no manufacturer and no bom number, i.e both cells are empty, then that bike does not have that component assigned, so just return NONE. This is not a bom error so it should not be logged as an error
        if not manu and not bom_number:
            return Part.objects.get(description="NONE")
        # Fill out any missing zeroes
        bom_number = self.add_zeroes(bom_number)
        # Try to get the part from database. If the part is not found then return Not Found object.
        part, created = Part.objects.get_or_create(
            agile_number=bom_number)
        return part

    def import_sbcproject(self, row):

        if row["Item Type (TOC)"] == "Engineered Assembly":
            sbc_project = SbcProject.objects.update_or_create(
                agile_number = row["Number"],
                defaults = {
                    "description": row["Description"]
                })[0]
            tla, created = Part.objects.get_or_create(
                agile_number=row["Item Number (TOC)"],
                defaults={
                    "lifecycle": row["Item Lifecycle Phase (TOC)"],
                    "description": row["Item Description (TOC)"]
                }    
            )
            sbc_project.tla.add(tla)
            return True
        elif row["Item Type (TOC)"] == "Test Report Part":
            sbc_project = SbcProject.objects.update_or_create(
                agile_number = row["Number"],
                defaults = {
                    "description": row["Description"]
                }
                )[0]
            trp, created = TestReportPart.objects.get_or_create(
                agile_number=row["Item Number (TOC)"],
                defaults={
                    "lifecycle": row["Item Lifecycle Phase (TOC)"],
                    "description": row["Item Description (TOC)"]
                }
            )
            sbc_project.trp.add(trp)
            return True
        else:
            return False
