"""
Расширенная версия игры Змейка для TouchDesigner
Включает дополнительные функции: уровни сложности, рекорды, бонусы
"""

import random
import time
import json
import os

class AdvancedSnakeGame:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.reset_game()
        self.high_score = self.load_high_score()
        
    def reset_game(self):
        """Сброс игры к начальному состоянию"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.level = 1
        self.food_eaten = 0
        self.bonus_food = None
        self.bonus_timer = 0
        self.speed_multiplier = 1.0
        
    def load_high_score(self):
        """Загрузка рекорда из файла"""
        try:
            if os.path.exists('snake_highscore.json'):
                with open('snake_highscore.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
        
    def save_high_score(self):
        """Сохранение рекорда в файл"""
        try:
            data = {'high_score': self.high_score}
            with open('snake_highscore.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
            
    def generate_food(self):
        """Генерация обычной еды"""
        while True:
            food = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if food not in self.snake and food != self.bonus_food:
                return food
                
    def generate_bonus_food(self):
        """Генерация бонусной еды"""
        if random.random() < 0.3:  # 30% шанс появления бонуса
            while True:
                bonus = (random.randint(0, self.width-1), random.randint(0, self.height-1))
                if bonus not in self.snake and bonus != self.food:
                    self.bonus_food = bonus
                    self.bonus_timer = 50  # Бонус исчезает через 50 ходов
                    break
                    
    def change_direction(self, new_direction):
        """Изменение направления движения змейки"""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
            
    def move(self):
        """Движение змейки с расширенной логикой"""
        if self.game_over:
            return
            
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Проверка на столкновение со стенами
        if (new_head[0] < 0 or new_head[0] >= self.width or 
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
            
        # Проверка на столкновение с собой
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
            
        self.snake.insert(0, new_head)
        
        # Проверка на поедание обычной еды
        if new_head == self.food:
            self.score += 10 * self.level
            self.food_eaten += 1
            self.food = self.generate_food()
            
            # Увеличение уровня каждые 5 еды
            if self.food_eaten % 5 == 0:
                self.level += 1
                self.speed_multiplier += 0.1
                
            # Шанс появления бонуса
            if random.random() < 0.2:
                self.generate_bonus_food()
        
        # Проверка на поедание бонусной еды
        elif new_head == self.bonus_food:
            self.score += 50 * self.level
            self.bonus_food = None
            self.bonus_timer = 0
        else:
            self.snake.pop()
            
        # Обновление таймера бонуса
        if self.bonus_timer > 0:
            self.bonus_timer -= 1
            if self.bonus_timer == 0:
                self.bonus_food = None
                
    def get_speed(self):
        """Получение текущей скорости игры"""
        base_speed = 0.5
        return max(0.1, base_speed - (self.level - 1) * 0.05)
        
    def get_game_field_advanced(self):
        """Получение расширенного игрового поля"""
        field = []
        
        # Создаем пустое поле
        for y in range(self.height):
            row = [' '] * self.width
            field.append(row)
            
        # Размещаем змейку
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                field[y][x] = 'O'  # Голова змейки
            else:
                field[y][x] = 'o'  # Тело змейки
                
        # Размещаем обычную еду
        field[self.food[1]][self.food[0]] = '*'
        
        # Размещаем бонусную еду
        if self.bonus_food:
            field[self.bonus_food[1]][self.bonus_food[0]] = '$'
            
        # Преобразуем в строки
        result = []
        result.append('=' * (self.width + 2))
        for row in field:
            result.append('|' + ''.join(row) + '|')
        result.append('=' * (self.width + 2))
        
        # Информационная панель
        result.append(f'Счет: {self.score}')
        result.append(f'Рекорд: {self.high_score}')
        result.append(f'Уровень: {self.level}')
        result.append(f'Съедено: {self.food_eaten}')
        
        if self.bonus_food:
            result.append(f'Бонус! Осталось: {self.bonus_timer}')
            
        if self.game_over:
            result.append('')
            result.append('ИГРА ОКОНЧЕНА!')
            if self.score == self.high_score and self.score > 0:
                result.append('НОВЫЙ РЕКОРД!')
            result.append('Нажмите R для перезапуска')
            
        return '\n'.join(result)

# TouchDesigner интеграция для расширенной версии
class TouchDesignerSnakeAdvanced:
    def __init__(self):
        self.game = AdvancedSnakeGame()
        self.last_update = time.time()
        
    def update(self):
        """Обновление с учетом динамической скорости"""
        current_time = time.time()
        speed_interval = self.game.get_speed()
        
        if current_time - self.last_update >= speed_interval:
            self.game.move()
            self.last_update = current_time
            
        return self.game.get_game_field_advanced()
        
    def handle_key(self, key):
        """Обработка клавиш"""
        if key == 'up':
            self.game.change_direction((0, -1))
        elif key == 'down':
            self.game.change_direction((0, 1))
        elif key == 'left':
            self.game.change_direction((-1, 0))
        elif key == 'right':
            self.game.change_direction((1, 0))
        elif key == 'r':
            self.game.reset_game()
            
    def get_game_stats(self):
        """Получение статистики для отображения в Table DAT"""
        return {
            'score': self.game.score,
            'high_score': self.game.high_score,
            'level': self.game.level,
            'food_eaten': self.game.food_eaten,
            'speed': self.game.get_speed(),
            'game_over': self.game.game_over
        }

# Глобальная переменная для расширенной игры
if 'advanced_game' not in globals():
    advanced_game = TouchDesignerSnakeAdvanced()

# Код для Text DAT (расширенная версия)
def get_advanced_display():
    """Возвращает расширенное отображение игры"""
    return advanced_game.update()

# Код для обработки клавиш (расширенная версия)
def handle_advanced_key(key_name):
    """Обработка клавиш для расширенной версии"""
    advanced_game.handle_key(key_name)

# Код для Table DAT со статистикой
def get_stats_table():
    """Возвращает статистику в формате для Table DAT"""
    stats = advanced_game.get_game_stats()
    
    # Формируем таблицу
    headers = ['Параметр', 'Значение']
    rows = [
        ['Счет', str(stats['score'])],
        ['Рекорд', str(stats['high_score'])],
        ['Уровень', str(stats['level'])],
        ['Съедено еды', str(stats['food_eaten'])],
        ['Скорость', f"{stats['speed']:.2f}"],
        ['Статус', 'Игра окончена' if stats['game_over'] else 'Игра идет']
    ]
    
    result = [headers]
    result.extend(rows)
    return result

# Функция для создания цветового отображения
def get_color_data():
    """Возвращает данные для цветового отображения в Script TOP"""
    game = advanced_game.game
    
    # Создаем цветовую карту
    color_map = {}
    
    # Змейка
    for i, pos in enumerate(game.snake):
        if i == 0:
            color_map[pos] = (255, 100, 100)  # Красная голова
        else:
            color_map[pos] = (100, 255, 100)  # Зеленое тело
            
    # Обычная еда
    color_map[game.food] = (255, 255, 100)  # Желтая еда
    
    # Бонусная еда
    if game.bonus_food:
        color_map[game.bonus_food] = (255, 100, 255)  # Фиолетовый бонус
        
    return color_map

print("Расширенная версия игры Змейка создана!")
print("\nДополнительные функции:")
print("- Система уровней (скорость увеличивается)")
print("- Бонусная еда ($) за 50 очков")
print("- Сохранение рекордов")
print("- Динамическая статистика")
print("- Цветовое отображение")