"""
TouchDesigner Setup для игры Змейка
Этот файл содержит код для различных компонентов TouchDesigner
"""

# =============================================================================
# КОД ДЛЯ TEXT DAT (для отображения игры)
# =============================================================================

# Скопируйте этот код в Text DAT:
text_dat_code = '''
# Импортируем основной модуль игры
exec(open('snake_game.py').read())

# Основная функция, которая будет вызываться для обновления текста
me.text = get_display_text()
'''

# =============================================================================
# КОД ДЛЯ TIMER CHOP (для автоматического движения змейки)
# =============================================================================

timer_chop_code = '''
# В Timer CHOP установите:
# Timer Type: Timer
# Length: 0.5 (скорость игры - 0.5 секунды между ходами)
# Auto Start: On
'''

# =============================================================================
# КОД ДЛЯ SCRIPT DAT (обработчик таймера)
# =============================================================================

script_dat_code = '''
def onPulse(channel):
    """Вызывается каждый раз при срабатывании таймера"""
    # Находим Text DAT с игрой
    text_dat = op('text1')  # Замените на имя вашего Text DAT
    
    # Обновляем игру
    exec(open('snake_game.py').read())
    text_dat.text = update_game()

def onValueChange(channel, sampleIndex, val, prev):
    pass
'''

# =============================================================================
# КОД ДЛЯ KEYBOARD IN CHOP (обработка клавиш)
# =============================================================================

keyboard_script_code = '''
def onValueChange(channel, sampleIndex, val, prev):
    """Обработка нажатий клавиш"""
    if val == 1.0:  # Клавиша нажата
        key_name = channel.name
        
        # Импортируем игру
        exec(open('snake_game.py').read())
        
        # Обрабатываем клавиши
        if key_name == 'up':
            game.change_direction((0, -1))
        elif key_name == 'down':
            game.change_direction((0, 1))
        elif key_name == 'left':
            game.change_direction((-1, 0))
        elif key_name == 'right':
            game.change_direction((1, 0))
        elif key_name == 'r':
            game.reset_game()
        
        # Обновляем отображение
        text_dat = op('text1')  # Замените на имя вашего Text DAT
        text_dat.text = game.get_game_field()

def onPulse(channel):
    pass
'''

# =============================================================================
# РАСШИРЕННАЯ ВЕРСИЯ С ГРАФИЧЕСКИМ ОТОБРАЖЕНИЕМ
# =============================================================================

class SnakeGameGraphical:
    """Версия игры для графического отображения через TOP"""
    
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.reset_game()
        
    def reset_game(self):
        """Сброс игры к начальному состоянию"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
    def generate_food(self):
        """Генерация еды в случайном месте"""
        import random
        while True:
            food = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if food not in self.snake:
                return food
                
    def change_direction(self, new_direction):
        """Изменение направления движения змейки"""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
            
    def move(self):
        """Движение змейки"""
        if self.game_over:
            return
            
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Проверка на столкновение со стенами
        if (new_head[0] < 0 or new_head[0] >= self.width or 
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return
            
        # Проверка на столкновение с собой
        if new_head in self.snake:
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        # Проверка на поедание еды
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
            
    def get_render_data(self):
        """Получение данных для рендеринга"""
        return {
            'snake': self.snake,
            'food': self.food,
            'score': self.score,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }

# Код для Script TOP (графический рендеринг)
script_top_code = '''
import numpy as np

def onCook(scriptOp):
    """Рендеринг игрового поля"""
    # Импортируем игру
    exec(open('touchdesigner_setup.py').read())
    
    if 'graphics_game' not in globals():
        globals()['graphics_game'] = SnakeGameGraphical()
    
    game = globals()['graphics_game']
    
    # Создаем изображение
    width, height = 400, 300
    image = np.zeros((height, width, 4), dtype=np.float32)
    
    # Фон
    image[:, :, 3] = 1.0  # Альфа
    
    cell_w = width // game.width
    cell_h = height // game.height
    
    # Рисуем змейку
    for i, (x, y) in enumerate(game.snake):
        x1, y1 = x * cell_w, y * cell_h
        x2, y2 = x1 + cell_w, y1 + cell_h
        
        if i == 0:  # Голова
            image[y1:y2, x1:x2, 0] = 0.8  # Красный
            image[y1:y2, x1:x2, 1] = 0.2
            image[y1:y2, x1:x2, 2] = 0.2
        else:  # Тело
            image[y1:y2, x1:x2, 0] = 0.2
            image[y1:y2, x1:x2, 1] = 0.8  # Зеленый
            image[y1:y2, x1:x2, 2] = 0.2
    
    # Рисуем еду
    fx, fy = game.food
    x1, y1 = fx * cell_w, fy * cell_h
    x2, y2 = x1 + cell_w, y1 + cell_h
    image[y1:y2, x1:x2, 0] = 1.0  # Желтый
    image[y1:y2, x1:x2, 1] = 1.0
    image[y1:y2, x1:x2, 2] = 0.0
    
    scriptOp.copyNumpyArray(image)

def onPulse(channel):
    pass
'''

print("Файлы для TouchDesigner созданы!")
print("\nИнструкции по настройке:")
print("1. Создайте Text DAT и скопируйте в него код из text_dat_code")
print("2. Создайте Timer CHOP с интервалом 0.5 секунды")
print("3. Создайте Script DAT и подключите к нему Timer CHOP")
print("4. Создайте Keyboard In CHOP и Script DAT для обработки клавиш")
print("5. Используйте стрелки для управления, R для перезапуска")