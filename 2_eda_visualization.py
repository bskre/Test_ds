import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Загружаем очищенные данные
df = pd.read_excel('cleaned_sales_full.xlsx')
monthly = pd.read_excel('monthly_total.xlsx')
by_cat = pd.read_excel('monthly_by_category.xlsx')

print("=== Ключевые insights ===")
print(f"Среднемесячные продажи: {monthly['Объем_кг'].mean():.0f} кг")
print(f"Максимум за месяц: {monthly['Объем_кг'].max():.0f} кг (месяц {monthly.loc[monthly['Объем_кг'].idxmax(), 'Месяц']} {monthly.loc[monthly['Объем_кг'].idxmax(), 'Год']})")
print(f"Минимум за месяц: {monthly['Объем_кг'].min():.0f} кг")

# ==================== ГРАФИКИ ====================

plt.figure(figsize=(14, 8))

# 1. Общие продажи по месяцам
plt.subplot(2, 2, 1)
plt.plot(monthly['Дата'], monthly['Объем_кг'], marker='o', linewidth=2)
plt.title('Общий объём продаж по месяцам (кг)')
plt.xlabel('Дата')
plt.ylabel('Объём, кг')
plt.grid(True)

# 2. Продажи по годам
plt.subplot(2, 2, 2)
yearly = monthly.groupby('Год')['Объем_кг'].sum()
yearly.plot(kind='bar', color='skyblue')
plt.title('Продажи по годам (кг)')
plt.ylabel('Объём, кг')
plt.grid(True, axis='y')

# 3. Сезонность (среднее по месяцам)
plt.subplot(2, 2, 3)
season = monthly.groupby('Месяц')['Объем_кг'].mean()
season.plot(kind='bar', color='lightgreen')
plt.title('Средние продажи по месяцам года')
plt.xlabel('Месяц')
plt.ylabel('Средний объём, кг')
plt.grid(True, axis='y')

# 4. Продажи по категориям (последние 3 года)
plt.subplot(2, 2, 4)
recent = by_cat[by_cat['Год'] >= 2023]
cat_pivot = recent.pivot_table(index=['Год','Месяц'], columns='Категория', values='Объем_кг', aggfunc='sum').fillna(0)
cat_pivot.sum().plot(kind='bar', color=['orange','blue','green','red','purple'])
plt.title('Продажи по категориям (2023–2025)')
plt.ylabel('Объём, кг')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('sales_analysis_charts.png', dpi=200, bbox_inches='tight')
print("\n✅ Графики сохранены в файл: sales_analysis_charts.png")

# Топ-категории
print("\nТоп категорий по объёму (кг):")
print(by_cat.groupby('Категория')['Объем_кг'].sum().sort_values(ascending=False))

# Сохраняем сводку
summary = monthly.describe()
summary.to_excel('sales_summary.xlsx')
print("\nСводная статистика сохранена в sales_summary.xlsx")