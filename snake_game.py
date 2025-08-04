"""
Игра Змейка для TouchDesigner
Используется в Text DAT для отображения игрового поля
"""

# Импорты для TouchDesigner
try:
    import random
except:
    import tdu
    random = tdu.Dependency("random")

try:
    import time
except:
    import tdu
    time = tdu.Dependency("time")

class SnakeGame:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.reset_game()
        
    def reset_game(self):
        """Сброс игры к начальному состоянию"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)  # Начальное направление - вправо
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
    def generate_food(self):
        """Генерация еды в случайном месте"""
        while True:
            food = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if food not in self.snake:
                return food
                
    def change_direction(self, new_direction):
        """Изменение направления движения змейки"""
        # Проверяем, что новое направление не противоположно текущему
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
            
    def get_game_field(self):
        """Получение игрового поля в виде текста для Text DAT"""
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
                
        # Размещаем еду
        field[self.food[1]][self.food[0]] = '*'
        
        # Преобразуем в строки
        result = []
        result.append('=' * (self.width + 2))
        for row in field:
            result.append('|' + ''.join(row) + '|')
        result.append('=' * (self.width + 2))
        result.append(f'Счет: {self.score}')
        
        if self.game_over:
            result.append('ИГРА ОКОНЧЕНА!')
            result.append('Нажмите R для перезапуска')
            
        return '\n'.join(result)

# Глобальная переменная игры
if 'game' not in globals():
    game = SnakeGame()

def onKeyboardEvent(key, state, modifiers):
    """Обработка нажатий клавиш в TouchDesigner"""
    if state == 'down':
        if key == 'Up':
            game.change_direction((0, -1))
        elif key == 'Down':
            game.change_direction((0, 1))
        elif key == 'Left':
            game.change_direction((-1, 0))
        elif key == 'Right':
            game.change_direction((1, 0))
        elif key == 'r' or key == 'R':
            game.reset_game()

def update_game():
    """Обновление игры - вызывается периодически"""
    game.move()
    return game.get_game_field()

# Функции для TouchDesigner DAT
def onPulse(channel):
    """Вызывается при получении импульса"""
    update_game()

def onValueChange(channel, sampleIndex, val, prev):
    """Вызывается при изменении значения"""
    pass

# Основная функция для получения текущего состояния игры
def get_display_text():
    """Возвращает текст для отображения в Text DAT"""
    return game.get_game_field()