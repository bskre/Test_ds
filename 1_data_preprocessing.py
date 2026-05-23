import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore')

# =============================================
# ЗАГРУЗКА ИЗ XLS ФАЙЛА
# =============================================

file_path = 'Кировский продажи СП 2020-2025 (1).xls'   # ← поменяй, если имя файла другое

# Читаем Excel файл
df = pd.read_excel(file_path, sheet_name='TDSheet')

print("Форма данных:", df.shape)
print("Колонки:", df.columns.tolist())
print("\nПервые 5 строк:")
print(df.head())

# =============================================
# ОЧИСТКА ДАННЫХ
# =============================================

# Приводим названия колонок к удобным
df.columns = ['Месяц_год', 'Номенклатура', 'Объем_шт', 'Объем_кг']

# Преобразуем строки в числа
df['Объем_шт'] = pd.to_numeric(df['Объем_шт'].astype(str).str.replace(',', '').str.strip(), errors='coerce')
df['Объем_кг'] = pd.to_numeric(df['Объем_кг'].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# Парсинг даты
def parse_date(text):
    text = str(text).strip()
    month_map = {
        'Январь':1, 'Февраль':2, 'Март':3, 'Апрель':4, 'Май':5, 'Июнь':6,
        'Июль':7, 'Август':8, 'Сентябрь':9, 'Октябрь':10, 'Ноябрь':11, 'Декабрь':12
    }
    for month_name, month_num in month_map.items():
        if month_name in text:
            year_match = re.search(r'(\d{4})', text)
            year = int(year_match.group(1)) if year_match else None
            if year:
                return pd.Timestamp(year=year, month=month_num, day=1)
    return pd.NaT

df['Дата'] = df['Месяц_год'].apply(parse_date)
df['Год'] = df['Дата'].dt.year
df['Месяц'] = df['Дата'].dt.month

# Категоризация
def get_category(name):
    name = str(name).lower()
    if 'стм кировский' in name or 'стм' in name:
        return 'СТМ Кировский'
    elif 'десертные' in name:
        return 'Десертные'
    elif 'сладкие' in name:
        return 'Сладкие'
    elif 'сгущенного' in name or 'сгущённого' in name:
        return 'Со вкусом сгущенки'
    elif 'земляники' in name:
        return 'Со вкусом земляники'
    elif 'бомбер' in name:
        return 'Шарики Бомбер'
    elif 'чебурашка' in name:
        return 'Чебурашка'
    else:
        return 'Другое'

df['Категория'] = df['Номенклатура'].apply(get_category)

# =============================================
# СОХРАНЕНИЕ
# =============================================

df.to_excel('cleaned_sales_full.xlsx', index=False)

# Итоговые таблицы
monthly_total = df.groupby(['Год', 'Месяц', 'Дата']).agg({
    'Объем_шт': 'sum',
    'Объем_кг': 'sum'
}).round(2).reset_index()

monthly_by_cat = df.groupby(['Год', 'Месяц', 'Категория'])['Объем_кг'].sum().round(2).reset_index()

monthly_total.to_excel('monthly_total.xlsx', index=False)
monthly_by_cat.to_excel('monthly_by_category.xlsx', index=False)

print("\n" + "="*60)
print("✅ УСПЕШНО ЗАВЕРШЕНО!")
print(f"Всего строк: {len(df)}")
print(f"Период: с {df['Дата'].min().strftime('%Y-%m')} по {df['Дата'].max().strftime('%Y-%m')}")
print("\nПродажи по годам (кг):")
print(df.groupby('Год')['Объем_кг'].sum().round(0).astype(int))