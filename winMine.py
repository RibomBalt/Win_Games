# -*- encoding:utf-8
import random


class minemap:
    '''
    关于扫雷游戏地图的类。
    '''
    map_status = {
        'MINE': 1,
        'NOT_MINE': 0,
    }

    show_status = {
        '0': '0',
        '1': '1',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        'UNKNOWN': '○',
        'ASSUME': '●',
        'UNSURE': '?',
        'STRIKE': '☢',
        'BOOM': '۞',
        'FALSE_ASSUME': '∅'
    }
    numbers='012345678'

    # TODO:未解决“初见杀”问题
    def __init__(self, x, y, mine=20):
        '''
        创建一个扫雷地图


        :param x:行数
        :param y:列数
        :param mine:雷数
        '''

        assert isinstance(x, int) and x > 0, 'Bad params'
        assert isinstance(y, int) and x > 0, 'Bad params'
        assert isinstance(mine, int) and mine > 0 and mine <= x * y, 'Bad params'

        self.x = x
        self.y = y
        self.mineNum = mine

        mine_site = random.sample(range(x * y), mine)

        self.map = {(i, j): self.map_status['MINE'] if i * y + j in mine_site else self.map_status['NOT_MINE']
                    for i in range(x) for j in range(y)}
        self.show = {(i, j): self.show_status['UNKNOWN'] for j in range(y) for i in range(x)}

    def __str__(self):
        '''
        打印扫雷地图
        :return: 扫雷地图字符串形式，print即可输出
        '''
        res = ['\t'.join([str(i) for i in range(self.y)]),'\t'.join(['|' for i in range(self.y)])]
        for i in range(self.x):
            char = []
            for j in range(self.y):
                char.append(self.show[(i, j)])
            char.append('-%d'%(i))
            res.append('\t'.join(char))
        return '\n'.join(res)

    def __getitem__(self, args):
        '''
        返回某个位置的地图状态（有无雷）和显示状态（如何显示）
        :param args:元组：(行, 列)
        :return:元组：(地图状态，显示状态)
        '''
        return (self.map[args], self.show[args])

    def _getNeighbor(self, x, y):
        '''
        返回某位置相邻所有格子的元组。

        :param x: 行
        :param y: 列
        :return: 包含所有相邻格子位置的filter对象
        '''
        preNeighbor = {(i, j) for i in range(x - 1, x + 2) for j in range(y - 1, y + 2)}
        return filter(lambda t: 0 <= t[0] < self.x and 0 <= t[1] < self.y and t != (x, y), preNeighbor)

    def _getNumber(self, x, y):
        '''
        返回某数字位置的数字。不携带任何异常情况。
        :param x: 行
        :param y: 列
        :return: 数字int
        '''
        # TODO 添加排错机制
        s = list(map(self.map.get, self._getNeighbor(x, y)))
        return s.count(self.map_status['MINE'])

    def flip(self, x, y):
        '''
        翻转某区域，相当于GUI左键。.

        若翻转已翻转区域、翻转了ASSUME、UNSURE区域，会assert，讯息：'KeyWarning'。
        :param x: 行
        :param y: 列
        :return: 若触发了雷/全部扫完返回False，否则True
        '''
        assert self.show[(x, y)] == self.show_status['UNKNOWN'], 'KeyWarning'
        toflip = {(x, y)}
        while toflip:
            site = toflip.pop()
            status = self[site]
            try:
                assert status[1] == self.show_status['UNKNOWN']
                if status[0] == self.map_status['MINE']:
                    # 显示最终地图
                    for pos, shows in self.show.items():
                        # isMine
                        if self.map[pos] == self.map_status['MINE']:
                            if pos == site:
                                self.show[pos] = self.show_status['STRIKE']
                            elif shows == self.show_status['ASSUME']:
                                pass
                            else:
                                self.show[pos] = self.show_status['BOOM']
                        # Not Mine
                        else:
                            if shows == self.show_status['ASSUME']:
                                self.show[pos] = self.show_status['FALSE_ASSUME']
                            else:
                                n = self._getNumber(*pos)
                                self.show[pos] = self.show_status[str(n)]
                    return False
                else:
                    n = self._getNumber(*site)
                    if n == 0:
                        # TODO 若性能不足，可以考虑在这里排除assert
                        toflip = toflip.union(set(self._getNeighbor(*site)))
                    self.show[site] = self.show_status[str(n)]
            except AssertionError as e:
                pass
        # 判断是否胜利：
        if (self.mineNum == 0) and (filter(lambda args:self[args][0]==self.map_status['MINE'] or self[args][1] in self.numbers,((i,j) for i in range(self.x) for j in range(self.y)))) and (
                    self.show_status['UNSURE'] not in self.show.values()):
            return False

        return True

    def assume(self, x, y):
        '''
        假定某区域是雷以佐证判断，同时雷数减一。相当于GUI右键一次.

        若assume在已经assume的位置，assert KeyWarning
        :param x:行
        :param y:列
        :return:True
        '''
        assert (self.show[(x, y)] == self.show_status['UNKNOWN']) or (
            self.show[(x, y)] == self.show_status['UNSURE']), 'KeyWarning'
        self.show[(x, y)] = self.show_status['ASSUME']
        self.mineNum -= 1
        return True

    def unsure(self, x, y):
        '''
        对某区域不确定的标记。相当于GUI右键两次.

        若unsure在已经unsure的位置，assert KeyWarning
        :param x:行
        :param y:列
        :return:True
        '''
        assert (self.show[(x, y)] == self.show_status['UNKNOWN']) or (
            self.show[(x, y)] == self.show_status['ASSUME']), 'KeyWarning'
        if self.show[(x, y)] == self.show_status['ASSUME']:
            self.mineNum += 1
        self.show[(x, y)] = self.show_status['UNSURE']
        return True

    def normal(self, x, y):
        '''
        取消某区域的assume和unsure标记，即回到unknown.

        若已经没有标记，assert KeyWarning
        :param x: 行
        :param y: 列
        :return: True
        '''
        assert (self.show[(x, y)] == self.show_status['UNSURE']) or (
            self.show[(x, y)] == self.show_status['ASSUME']), 'KeyWarning'
        if self.show[(x, y)] == self.show_status['ASSUME']:
            self.mineNum += 1
        self.show[(x, y)] = self.show_status['UNKNOWN']
        return True

    def assertion(self, x, y):
        '''
        高级操作，相当于双键操作.

        当某点为已知数字1-7，且周围的ASSUME标记超过了数字，
        且周围没有unsure标记时，对周围所有的位置调用flip()
        当违反以上条件时，assert KeyWarning
        :param x: 行
        :param y: 列
        :return: 若触发了雷/全部扫完返回False，否则True
        '''
        assert (self.show[(x, y)] in '12345678'), 'KeyWarning'
        neighbors = set(filter(lambda p: p != (x, y), set(self._getNeighbor(x, y))))
        assumeNum = 0
        for pos in neighbors:
            app = self.show[pos]
            assert app != self.show_status['UNSURE'], 'KeyWarning'
            if app == self.show_status['ASSUME']:
                assumeNum += 1
        assert assumeNum >= int(self.show[(x, y)])

        while neighbors:
            try:
                if not self.flip(*neighbors.pop()):
                    return False

            except AssertionError as e:
                pass
        return True


if __name__ == '__main__':
    print('欢迎来到扫雷！本游戏由Cobalt编码实现。')
    s = input('请输入行数、列数、雷数，用空格隔开：')

    while True:
        try:
            winmine = minemap(*map(int, s.split()))
            break
        except:
            print('输入错误！请重新输入！')
            s = input('请输入行数、列数、雷数，用空格隔开：')

    helping = \
        '指令格式：指令头 行数 列数，用空格分隔\n' \
        '行数、列数从0开始\n' \
        '指令头列表：flip-单击某处空白;assume-右键标记为雷;unsure-右键标记为问号;normal-取消标记;assert-双键操作\n' \
        'help-重新显示此帮助;mine-显示当前雷数'


    def help(x=0, y=0):
        '''
        辅助函数，用于保证进程进行
        :param x:无用
        :param y: 无用
        :return: TRUE
        '''
        print(helping)
        return True


    def getMine(x=0, y=0):
        '''
        辅助函数
        :param x: 无用
        :param y: 无用
        :return: TRUE
        '''
        print('剩余雷数：%d。注意：不一定是真实剩余雷数！' % (winmine.mineNum))
        return True


    command_head = {
        'flip': winmine.flip,
        'assume': winmine.assume,
        'unsure': winmine.unsure,
        'normal': winmine.normal,
        'assert': winmine.assertion,
        'help': help,
        'mine': getMine
    }
    print(helping)
    print(winmine)
    command = input('请输入指令：')
    while True:
        command_list = command.split()
        try:
            assert command_list[0] in command_head.keys()

            if command_list[0] in {'help', 'mine'}:
                x = y = 0
            else:
                x = int(command_list[1])
                y = int(command_list[2])
                assert 0 <= x < winmine.x
                assert 0 <= y < winmine.y
            isContinue = command_head[command_list[0]](x, y)
        except:
            command = input('错误指令！请重新输入！需要帮助请输入help！\n请输入指令：')
            continue

        if not isContinue:
            break
        else:
            print(winmine)
            command = input('请输入指令：')
    print('游戏结束！')
    if winmine.show_status['STRIKE'] in winmine.show.values():
        print('你失败了！')
    else:
        print('你胜利了！')
    print(winmine)
    input('输入回车以退出')
