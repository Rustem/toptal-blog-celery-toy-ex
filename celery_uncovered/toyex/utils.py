import csv


def make_csv(filename, lines):
    with open(filename, 'wb') as csvfile:
        trending_csv = csv.writer(csvfile)
        for line in lines:
            trending_csv.writerow(line)
    return filename
