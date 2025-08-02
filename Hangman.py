import os
import random
import configparser
from time import sleep
from dict_parser import parse_txt_to_dict

class HangmanGame:
    def __init__(self):
        # 读取配置文件
        while True:
            try:
                config = self.load_config()
                self.rounds = config.getint('Settings', 'rounds')
                self.wrong_max = config.getint('Settings', 'wrong_max')
                self.word_dict_path = config.get('Settings', 'word_dict_path')
                self.word_dict = parse_txt_to_dict(self.word_dict_path)  # 导入词库
                break
            except (configparser.Error, FileNotFoundError, ValueError) as e:
                if str(e).startswith("词库文件不存在"):
                    print(f"[词库文件不存在: {self.word_dict_path}，生成默认词库]")
                    with open('default.txt', 'w', encoding='utf-8') as txt:
                        txt.write('apple 苹果\nbanana 香蕉\ncherry 樱桃\ndog 狗\negg 鸡蛋\nfish 鱼\ngrape 葡萄\nhorse 马')
                        self.create_default_ini('settings.ini', 'default.txt')
                else:
                    self.create_default_ini('settings.ini')

        # 游戏状态
        self.answers = []
        self.ans = ''
        self.definition = ''
        self.wrong = 0
        self.guessed = []
        self.game_over = False
        self.won = False
        self.high_score = 0
        self.score = 0
        
        # 重置游戏状态
        self.reset(totally=True)

    @staticmethod
    def load_config(ini_path='settings.ini'):
        """读取配置文件"""
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8')
        return config

    @staticmethod
    def create_default_ini(ini_path, word_dict_path='lib/CET4_edited.txt'):
        """创建默认的配置文件"""
        default_config = f'[Settings]\nword_dict_path = {word_dict_path}\nrounds = 5\nwrong_max = 6'
        with open(ini_path, 'w', encoding='utf-8') as ini:
            ini.write(default_config)

    def reset(self, totally=False):
        """重置游戏状态"""
        if totally:
            self.answers = random.sample(list(self.word_dict.keys()), self.rounds)
            self.score = 0
            os.system('cls')
        self.ans = self.answers.pop()  # 从词典中随机选择一个单词
        self.definition = self.word_dict[self.ans]
        self.wrong = 0
        self.guessed = []
        self.game_over = False
        self.won = False

    def display_hangman(self):
        """显示绞刑架图案"""
        stages = [
            '''
                   |
                   |
                   |''',
            '''
               O   |
                   |
                   |''',
            '''
               O   |
               |   |
                   |''',
            '''
               O   |
              /|   |
                   |''',
            r'''
               O   |
              /|\  |
                   |''',
            r'''
               O   |
              /|\  |
              /    |''',
            r'''
               O   |
              /|\  |
              / \  |''',
            '''
               -----
               |   |''',
            '''
                   |
            =========='''
        ]
        return stages[-2] + stages[self.wrong] + stages[-1]

    def display_word(self):
        """显示当前猜测进度"""
        display = ''
        for letter in self.ans:
            if any(letter == g[0] and g[1] for g in self.guessed if len(g[0]) == 1):
                display += letter
            else:
                display += '_'
        return display.strip()

    def display_info(self, round_num):
        """显示游戏状态"""
        print('\033[1J', '\033[1;1H', sep='', end='')  # 清屏
        print(f'[第{round_num + 1}轮游戏]')

        print(self.display_hangman())

        print(f'\n当前单词({len(self.ans)}): {self.display_word()} ({self.definition})')

        if self.guessed:
            formatted = []
            for g in sorted(self.guessed, key=lambda x: (not x[1], x[0])):
                # 输出已猜字母，对的绿色，错的灰色
                if len(g[0]) == 1:
                    if g[1]:
                        formatted.append(f'\033[92m{g[0]}\033[0m')
                    else:
                        formatted.append(f'\033[2m{g[0]}\033[0m')

                # 如果是已猜单词，每个位置对的字母显示绿色，否则灰色
                else:
                    word = ''
                    for i, ch in enumerate(g[0]):
                        if i < len(self.ans) and ch == self.ans[i]:
                            word += f'\033[92m{ch}\033[0m'
                        else:
                            word += f'\033[2m{ch}\033[0m'
                    formatted.append(word)

            print(f'已猜: {', '.join(formatted)}')

        print(f'剩余错误次数: {self.wrong_max - self.wrong}')
        print(f'当前分数: {self.score}\n')

    def check_guess(self, guess):
        """验证用户输入是否合法"""
        if len(guess) == 1 and guess.isalpha():
            return True
        if len(guess) == len(self.ans) and guess.isalpha():
            return True
        return False

    def make_guess(self, guess):
        """处理用户猜测"""
        if guess == '\t':
            return
        guess = guess.strip().lower()

        # 处理整个单词的猜测
        if len(guess) == len(self.ans):
            if guess in [g[0] for g in self.guessed if len(g[0]) == len(self.ans)]:
                print(f'\033[34m♻ 你已经猜过单词 {guess} 了！\033[0m')
                sleep(1)
                return

            score = 0
            for i, c in enumerate(guess):
                if self.ans[i] == c and (c, True) not in self.guessed:
                    score += 1
                    if guess != self.ans:  # 对的字母也单独加入guessed，防止误给连击奖励
                        self.guessed.append((c, True))
            if score > 1:
                no_combo = 0 if self.guessed and self.guessed[-1][1] else 1
                print(f'\033[32m[命中奖励] +{score - no_combo}分\033[0m')
                self.score += score - no_combo
                sleep(1)

            if guess == self.ans:
                self.combo()
                self.guessed.append((guess, True))
                self.won = True
                self.game_over = True
            else:
                print(f'\033[31m✖单词 {guess} 错误。\033[0m')
                sleep(1)
                self.guessed.append((guess, False))
                self.wrong += 1
            return

        # 处理单个字母的猜测
        if guess in [g[0] for g in self.guessed if len(g[0]) == 1]:
            print(f'\033[34m♻ 你已经猜过字母 {guess} 了！\033[0m')
            sleep(1)
            return
        if guess in self.ans:
            print(f'\033[32m✔ 字母 {guess} 在单词中。\033[0m')
            self.combo()
            self.guessed.append((guess, True))
            sleep(1)
        else:
            print(f'\033[31m✖ 字母 {guess} 不在单词中。\033[0m')
            self.guessed.append((guess, False))
            self.wrong += 1
            sleep(1)

        # 检查是否猜对单词：看答案中的每个字母是否都在已猜字母中
        if all(letter in [g[0] for g in self.guessed if len(g[0]) == 1] for letter in self.ans):
            self.won = True
            self.game_over = True
        elif self.wrong >= self.wrong_max:
            self.game_over = True

    def combo(self):
        if self.guessed and self.guessed[-1][1]:
            print(f'\033[32m[连击奖励] +1分\033[0m')
            self.score += 1

    def round_end(self, round_num):
        """游戏一轮结束"""
        if self.won:
            print(f'🎉 猜对了！恭喜本轮胜利！({self.ans} - {self.definition})')
            if self.wrong < self.wrong_max:
                print(f'\033[32m[错误次数结余] +{self.wrong_max - self.wrong}分\033[0m')
                self.score += self.wrong_max - self.wrong

            if all(g[1] for g in self.guessed):
                print(f'\033[32m[无伤奖励] +{len(self.ans)}分\033[0m')  # 无伤通关的得分=单词长度=1+Σ连击奖励
                self.score += len(self.ans)

        else:
            print('💀 本轮游戏失败！你被绞死了！')
            print(f'正确答案是: {self.ans} ({self.definition})')
            print(f'\033[31m[本轮失败] +0分\033[0m')

        if round_num < self.rounds - 1:  # 防止玩家直接结束了最后一轮看不见结果
            print(f'\n第{round_num + 1}轮游戏结束！')
            print(f'目前总分: {self.score}，每轮平均得分: {self.score / (round_num + 1):.1f}')
            return input('\n回车↩︎ 继续 / Tab+回车↩︎ 结束游戏...')
        else:
            print(f'\n最后一轮游戏结束！')
            input('\n回车↩︎ 继续...')
            return '\t'

    def play(self):
        """主游戏循环"""
        print('\033[2J', '\033[1;1H', sep='', end='')  # 清屏
        print(f'欢迎来到 Hangman Game!\n历史高分: {self.high_score}\n{'=' * 40}')
        print(f'规则：\n猜出隐藏的英文单词，字母不分大小写，有{self.wrong_max}次错误机会。')
        print(f'游戏共{self.rounds}轮，全部结束后计算每轮平均分。\n')
        print(f'注意：\n游戏配置在exe同目录下的settings.ini中，可自定义词库等游戏设置，删除可恢复默认设置。')
        print(f'正在使用词库：{self.word_dict_path}。\n')
        input('回车↩︎ 开始游戏...')

        round_num = 0
        for round_num in range(self.rounds):
            user_input: str
            while True:
                # 显示游戏状态
                self.display_info(round_num)

                # 检查游戏状态
                if self.game_over:
                    user_input = self.round_end(round_num)
                    break
                else:
                    # 用户输入
                    while True:
                        guess = input(f'(Tab+回车↩︎ 有偿提示)请输入单个字母/整个单词: ')
                        if self.check_guess(guess.strip()):
                            break
                        elif guess == '\t':
                            self.hint()
                            break

                        print('\033[1A\033[2K\r输入有误！', end='')
                        sleep(1)
                        print('\033[2K\r', end='')

                    # 处理猜测
                    self.make_guess(guess)

            # 检查是否提前结束游戏
            if '\t' in user_input:
                break

            self.reset()

        print('\n游戏结束！')
        self.high_score = max(self.score, self.high_score)
        avg = self.score / (round_num + 1)
        print(f'游戏共进行{round_num + 1}轮，总分: {self.score}/最高{self.high_score}，每轮平均得分: {avg:.2f}，', end='')
        print(f'{'一般' if avg < 10 else '不错' if avg < 13 else '厉害' if avg < 16 else '优秀' if avg < 18 else '顶级'}')
        return input('\n回车↩︎ 继续 / Tab+回车↩︎ 结束游戏...')

    def hint(self):
        """提示"""
        lib = [x for x in self.ans if x not in [g[0] for g in self.guessed if len(g[0]) == 1]]
        if self.score < 2:
            print(f'\033[31m[提示失败] 分数不足\033[0m')
            sleep(1)
            return
        if not lib:
            print(f'\033[31m[提示失败] 已无字母可提示\033[0m')
            sleep(1)
            return

        c = random.sample(lib, 1)[0]
        print(f'\033[34m[有偿提示] -2分')
        print(f'提示字母: {c}\033[0m')
        self.score -= 2
        input('\n回车↩︎ 继续...')

def main():
    """主函数"""
    game = HangmanGame()
    while '\t' not in game.play():
        game.reset(totally=True)


if __name__ == '__main__':
    main()
