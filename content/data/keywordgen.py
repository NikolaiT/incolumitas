cities = ['Detroit', 'El Paso', 'Memphis', 'Seattle', 'Denver',
 'Washington', 'Boston', 'Baltimore', 'Oklahoma City', 'Albuquerque']

law_fields = ['DUI law', 'criminal law', 'employment law',
 'family law', 'immigration lawyer', 'civil law', 'real estate attorney']

combinations = []

for city in cities:
	for field in law_fields:
		combinations.append('{} {}\n'.format(field, city))


with open('law_keywords.txt', 'w') as f:
	f.writelines(combinations)