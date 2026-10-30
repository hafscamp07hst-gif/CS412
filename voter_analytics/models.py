# File: voter_analytics/models.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/30/2026
# Description: Store voter records and load them from the Newton CSV file.

from django.conf import settings
from django.db import models


class Voter(models.Model):
    """Store the personal information and election history of one voter."""

    # Identify the voter and residential address.
    last_name = models.TextField()
    first_name = models.TextField()
    street_number = models.TextField()
    street_name = models.TextField()
    apartment_number = models.TextField(blank=True)
    zip_code = models.TextField()

    # Store dates, the two-character party code, and precinct.
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.TextField()

    # Record participation in each election and the total voter score.
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        """Return the voter's name and street address."""
        return (f'{self.first_name} {self.last_name}, '
                f'{self.street_number} {self.street_name}')


def load_data():
    """Load the Newton CSV into an empty Voter table; skip invalid records."""
    # Preserve existing records and prevent duplicates on another import.
    if len(Voter.objects.all()) > 0:
        print('Voter records already exist. No records were added or deleted.')
        return

    filename = settings.BASE_DIR / 'newton_voters.csv'
    f = open(filename)
    f.readline() # discard headers
    created = 0
    skipped = 0

    # Read each record using the file loop from the class example.
    for line in f:
        fields = line.strip().split(',')
        try:
            # Keep party-code spaces and convert TRUE/FALSE to booleans.
            voter = Voter(
                last_name=fields[1],
                first_name=fields[2],
                street_number=fields[3],
                street_name=fields[4],
                apartment_number=fields[5],
                zip_code=fields[6],
                date_of_birth=fields[7],
                date_of_registration=fields[8],
                party_affiliation=fields[9],
                precinct_number=fields[10],
                v20state=fields[11] == 'TRUE',
                v21town=fields[12] == 'TRUE',
                v21primary=fields[13] == 'TRUE',
                v22general=fields[14] == 'TRUE',
                v23town=fields[15] == 'TRUE',
                voter_score=fields[16],
            )
            voter.save() # commit to database
            created += 1
        except:
            # Follow the class example by reporting records that cannot save.
            skipped += 1
            print(f'Skipped CSV record {created + skipped}: '
                  f'birth date={fields[7]}, registration date={fields[8]}')

    f.close()
    print(f'Done. Created {created} Voters. Skipped {skipped} records.')
