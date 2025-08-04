"""
Игра Змейка для TouchDesigner (без внешних зависимостей)
Использует встроенные функции TouchDesigner
"""

class SnakeGameTD:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.seed = 1234567  # Начальное значение для генератора случайных чисел
        self.reset_game()
        
    def simple_random(self, max_val):
        """Простой генератор псевдослучайных чисел"""
        self.seed = (self.seed * 1103515245 + 12345) & 0x7fffffff
        return self.seed % max_val
        
    def reset_game(self):
        """Сброс игры к начальному состоянию"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)  # Начальное направление - вправо
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
    def generate_food(self):
        """Генерация еды в случайном месте"""
        attempts = 0
        while attempts < 100:  # Ограничиваем попытки
            food_x = self.simple_random(self.width)
            food_y = self.simple_random(self.height)
            food = (food_x, food_y)
            if food not in self.snake:
                return food
            attempts += 1
        # Если не удалось найти место, размещаем в углу
        return (0, 0)
                
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
            if 0 <= x < self.width and 0 <= y < self.height:
                if i == 0:
                    field[y][x] = 'O'  # Голова змейки
                else:
                    field[y][x] = 'o'  # Тело змейки
                
        # Размещаем еду
        if 0 <= self.food[0] < self.width and 0 <= self.food[1] < self.height:
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

# Глобальная переменная игры для TouchDesigner
if not hasattr(me.parent(), 'snakeGame'):
    me.parent().snakeGame = SnakeGameTD()

game = me.parent().snakeGame

def update_game():
    """Обновление игры - вызывается периодически"""
    game.move()
    return game.get_game_field()

def handle_key(key_name):
    """Обработка нажатий клавиш"""
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

def get_display_text():
    """Возвращает текст для отображения в Text DAT"""
    return game.get_game_field()

# Функции для TouchDesigner callbacks
def onPulse(channel):
    """Вызывается при получении импульса"""
    update_game()

def onValueChange(channel, sampleIndex, val, prev):
    """Вызывается при изменении значения"""
    if val == 1.0:  # Клавиша нажата
        key_name = channel.name
        handle_key(key_name)

# Для использования в Text DAT
me.text = get_display_text()