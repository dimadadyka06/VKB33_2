import requests
import matplotlib.pyplot as plt

base_url = 'https://pokeapi.co/api/v2/'
limit = 10
url = f'{base_url}pokemon?limit={limit}'
response = requests.get(url)
pokemon_list = response.json()['results'] # преобразование json в словарь

data = []
for pokemon in pokemon_list:
    details = requests.get(pokemon['url']).json() # второй запрос к URL покемона чтоб получить больше сведений
    pokemon_info = {
        'id': details['id'],
        'name': details['name'],
        'height': details['height'],
        'weight': details['weight'],
        'hp': details['stats'][0]['base_stat'],
        'attack': details['stats'][1]['base_stat'],
        'defense': details['stats'][2]['base_stat'],
        'speed': details['stats'][5]['base_stat'],
        'special_defense': details['stats'][4]['base_stat']
    }
    data.append(pokemon_info)
print(data)
names = [p['name'].capitalize() for p in data]
ids = [p['id'] for p in data]
hps = [p['hp'] for p in data]
attacks = [p['attack'] for p in data]
defenses = [p['defense'] for p in data]
weights = [p['weight'] for p in data]
speeds = [p['speed'] for p in data]
special_defenses = [p['special_defense'] for p in data]




plt.figure(figsize=(15, 10))

# Линейный график
plt.subplot(2, 3, 1)
plt.plot(ids, hps, 'b-o', linewidth=2)
plt.xlabel('ID покемона')
plt.ylabel('HP')
plt.title('HP покемонов')
plt.grid(True, alpha=0.3)

# Точечная диаграмма
plt.subplot(2, 3, 2)
plt.scatter(attacks, defenses, c=ids, cmap='viridis', s=50)
plt.xlabel('Атака')
plt.ylabel('Защита')
plt.title('Атака vs Защита')
plt.colorbar(label='ID')

# Столбчатая диаграмма
plt.subplot(2, 3, 3)
plt.bar(names, weights, color='lightcoral')
plt.xlabel('Покемон')
plt.ylabel('Вес')
plt.title('Вес покемонов')
plt.xticks(rotation=45, ha='right')

# Горизонтальная столбчатая
plt.subplot(2, 3, 4)
plt.barh(names, speeds, color='lightgreen')
plt.xlabel('Скорость')
plt.ylabel('Покемон')
plt.title('Скорость покемонов')

# Гистограмма
plt.subplot(2, 3, 5)
plt.hist(attacks, bins=6, color='gold', edgecolor='black')
plt.xlabel('Атака')
plt.ylabel('Количество')
plt.title('Распределение атаки')

# Круговая диаграмма
plt.subplot(2, 3, 6)
low_sd = sum(1 for sd in special_defenses if sd < 50)
medium_sd = sum(1 for sd in special_defenses if 50 <= sd <= 80)
high_sd = sum(1 for sd in special_defenses if sd > 80)
sd_counts = [low_sd, medium_sd, high_sd]
labels = ['Низкая (<50)', 'Средняя (50-80)', 'Высокая (>80)']
colors = ['lightblue', 'lightcoral', 'gold']
plt.pie(sd_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('Категории специальной защиты')

plt.tight_layout()
plt.show()