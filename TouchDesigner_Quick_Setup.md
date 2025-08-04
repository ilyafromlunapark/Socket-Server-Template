# Быстрая настройка Змейки в TouchDesigner

## Шаг 1: Создайте Text DAT
1. Добавьте **Text DAT** в сеть
2. Скопируйте содержимое файла `snake_game_touchdesigner.py` в Text DAT

## Шаг 2: Создайте Timer CHOP
1. Добавьте **Timer CHOP**
2. Установите параметры:
   - Timer Type: `Timer`
   - Length: `0.5` (скорость игры)
   - Auto Start: `On`

## Шаг 3: Создайте Script DAT для обновления
1. Добавьте **Script DAT**
2. Подключите Timer CHOP к Script DAT (перетащите выход Timer CHOP на Script DAT)
3. В Script DAT введите:

```python
def onPulse(channel):
    # Найдите ваш Text DAT (замените 'text1' на правильное имя)
    text_dat = op('text1')
    
    # Обновляем игру
    text_dat.cook(force=True)

def onValueChange(channel, sampleIndex, val, prev):
    pass
```

## Шаг 4: Настройте управление клавишами
1. Добавьте **Keyboard In CHOP**
2. В параметрах Keys добавьте: `up down left right r`
3. Добавьте еще один **Script DAT**
4. Подключите Keyboard In CHOP к новому Script DAT
5. В этот Script DAT введите:

```python
def onValueChange(channel, sampleIndex, val, prev):
    if val == 1.0:  # Клавиша нажата
        key_name = channel.name
        
        # Найдите ваш Text DAT (замените 'text1' на правильное имя)
        text_dat = op('text1')
        
        # Используем функцию из Text DAT
        text_dat.module.handle_key(key_name)
        text_dat.cook(force=True)

def onPulse(channel):
    pass
```

## Управление:
- **↑** - Вверх
- **↓** - Вниз  
- **←** - Влево
- **→** - Вправо
- **R** - Перезапуск

## Если что-то не работает:
1. Проверьте имена операторов в `op('text1')`
2. Убедитесь, что Timer CHOP и Keyboard In CHOP правильно подключены к Script DAT
3. Проверьте, что в Text DAT нет ошибок (посмотрите в Text Port)

## Альтернативный простой код для Text DAT:

Если основной код не работает, используйте этот упрощенный вариант:

```python
# Упрощенная змейка
if not hasattr(me.parent(), 'snake'):
    me.parent().snake = [(10, 7)]
    me.parent().direction = (1, 0)
    me.parent().food = (15, 10)
    me.parent().score = 0
    me.parent().game_over = False

def move_snake():
    if me.parent().game_over:
        return
    
    head = me.parent().snake[0]
    new_head = (head[0] + me.parent().direction[0], head[1] + me.parent().direction[1])
    
    # Проверка границ
    if new_head[0] < 0 or new_head[0] >= 20 or new_head[1] < 0 or new_head[1] >= 15:
        me.parent().game_over = True
        return
    
    me.parent().snake.insert(0, new_head)
    
    # Проверка еды
    if new_head == me.parent().food:
        me.parent().score += 10
        # Новая еда
        me.parent().food = ((me.parent().score // 10 * 7) % 20, (me.parent().score // 10 * 3) % 15)
    else:
        me.parent().snake.pop()

# Отображение
field = []
for y in range(15):
    row = [' '] * 20
    field.append(row)

for i, (x, y) in enumerate(me.parent().snake):
    if 0 <= x < 20 and 0 <= y < 15:
        field[y][x] = 'O' if i == 0 else 'o'

if 0 <= me.parent().food[0] < 20 and 0 <= me.parent().food[1] < 15:
    field[me.parent().food[1]][me.parent().food[0]] = '*'

result = ['=' * 22]
for row in field:
    result.append('|' + ''.join(row) + '|')
result.append('=' * 22)
result.append(f'Счет: {me.parent().score}')

if me.parent().game_over:
    result.append('ИГРА ОКОНЧЕНА!')

me.text = '\n'.join(result)
```